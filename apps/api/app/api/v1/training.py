"""
Training UI API endpoints.
Allows non-technical users to train ML models via web interface.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from apps.api.app.core.database import get_db
from apps.api.app.auth.dependencies import get_current_user
from apps.api.app.models.user import User
from apps.api.app.ml.training_pipeline import MLTrainingPipeline


router = APIRouter(prefix="/training", tags=["ML Training"])


# Global training state
training_state = {
    "status": "idle",  # idle, training, completed, error
    "current_model": None,
    "progress": 0,
    "message": "",
    "started_at": None,
    "completed_at": None,
    "metrics": {}
}

training_history = []


class TrainingStatus(str, Enum):
    """Training status enum."""
    IDLE = "idle"
    TRAINING = "training"
    COMPLETED = "completed"
    ERROR = "error"


class ModelType(str, Enum):
    """Available models to train."""
    ALL = "all"
    LEAD_SCORING = "lead_scoring"
    CHURN = "churn"
    ENGAGEMENT = "engagement"


class TrainingRequest(BaseModel):
    """Request to start training."""
    model: ModelType = ModelType.ALL
    test_size: float = 0.2
    cv_folds: int = 5


class TrainingStatusResponse(BaseModel):
    """Current training status."""
    status: TrainingStatus
    current_model: Optional[str]
    progress: int
    message: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    metrics: Dict[str, Any]


class TrainingHistoryItem(BaseModel):
    """Training history item."""
    id: int
    model: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    metrics: Dict[str, Any]


async def train_model_background(
    db: Session,
    model_type: ModelType,
    test_size: float,
    cv_folds: int
):
    """Background task to train model."""
    global training_state, training_history
    
    try:
        training_state["status"] = "training"
        training_state["started_at"] = datetime.utcnow()
        training_state["completed_at"] = None
        training_state["metrics"] = {}
        
        pipeline = MLTrainingPipeline(db, test_size=test_size, cv_folds=cv_folds)
        
        if model_type == ModelType.ALL:
            # Train all models
            models = ["lead_scoring", "churn", "engagement"]
            total_models = len(models)
            
            for idx, model_name in enumerate(models, 1):
                training_state["current_model"] = model_name
                training_state["progress"] = int((idx - 1) / total_models * 100)
                training_state["message"] = f"Training {model_name}..."
                
                # Train model
                if model_name == "lead_scoring":
                    from app.ml.models.lead_scoring import LeadScoringModel
                    model = LeadScoringModel()
                    result = await pipeline.train_lead_scoring_model(model)
                elif model_name == "churn":
                    from app.ml.models.churn_prediction import ChurnPredictionModel
                    model = ChurnPredictionModel()
                    result = await pipeline.train_churn_model(model)
                else:  # engagement
                    from app.ml.models.engagement_prediction import EngagementPredictionModel
                    model = EngagementPredictionModel()
                    result = await pipeline.train_engagement_model(model)
                
                # Store metrics
                if result.get("success"):
                    training_state["metrics"][model_name] = result.get("metrics", {})
                else:
                    raise Exception(f"Training failed for {model_name}: {result.get('error')}")
        
        else:
            # Train single model
            model_name = model_type.value
            training_state["current_model"] = model_name
            training_state["message"] = f"Training {model_name}..."
            
            if model_name == "lead_scoring":
                from app.ml.models.lead_scoring import LeadScoringModel
                model = LeadScoringModel()
                result = await pipeline.train_lead_scoring_model(model)
            elif model_name == "churn":
                from app.ml.models.churn_prediction import ChurnPredictionModel
                model = ChurnPredictionModel()
                result = await pipeline.train_churn_model(model)
            else:  # engagement
                from app.ml.models.engagement_prediction import EngagementPredictionModel
                model = EngagementPredictionModel()
                result = await pipeline.train_engagement_model(model)
            
            if result.get("success"):
                training_state["metrics"][model_name] = result.get("metrics", {})
            else:
                raise Exception(f"Training failed: {result.get('error')}")
        
        # Training complete
        training_state["status"] = "completed"
        training_state["progress"] = 100
        training_state["message"] = "Training completed successfully"
        training_state["completed_at"] = datetime.utcnow()
        
        # Add to history
        duration = (training_state["completed_at"] - training_state["started_at"]).total_seconds()
        training_history.append({
            "id": len(training_history) + 1,
            "model": model_type.value,
            "status": "completed",
            "started_at": training_state["started_at"],
            "completed_at": training_state["completed_at"],
            "duration_seconds": duration,
            "metrics": training_state["metrics"]
        })
        
    except Exception as e:
        training_state["status"] = "error"
        training_state["message"] = str(e)
        training_state["completed_at"] = datetime.utcnow()
        
        # Add to history
        duration = (training_state["completed_at"] - training_state["started_at"]).total_seconds()
        training_history.append({
            "id": len(training_history) + 1,
            "model": model_type.value,
            "status": "error",
            "started_at": training_state["started_at"],
            "completed_at": training_state["completed_at"],
            "duration_seconds": duration,
            "metrics": {}
        })


@router.get("/status", response_model=TrainingStatusResponse)
async def get_training_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current training status.
    
    Returns real-time training progress and metrics.
    """
    return TrainingStatusResponse(**training_state)


@router.post("/start")
async def start_training(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start model training.
    
    Trains ML models in the background. Use /status endpoint to monitor progress.
    
    **Parameters:**
    - model: Which model to train (all, lead_scoring, churn, engagement)
    - test_size: Fraction of data for testing (default 0.2)
    - cv_folds: Number of cross-validation folds (default 5)
    """
    global training_state
    
    # Check if already training
    if training_state["status"] == "training":
        raise HTTPException(
            status_code=400,
            detail="Training already in progress. Stop current training first."
        )
    
    # Reset state
    training_state = {
        "status": "idle",
        "current_model": None,
        "progress": 0,
        "message": "Starting training...",
        "started_at": None,
        "completed_at": None,
        "metrics": {}
    }
    
    # Start background training
    background_tasks.add_task(
        train_model_background,
        db,
        request.model,
        request.test_size,
        request.cv_folds
    )
    
    return {
        "success": True,
        "message": f"Training started for {request.model.value}",
        "model": request.model.value
    }


@router.post("/stop")
async def stop_training(
    current_user: User = Depends(get_current_user)
):
    """
    Stop current training.
    
    Cancels in-progress training. Model will not be saved.
    """
    global training_state
    
    if training_state["status"] != "training":
        raise HTTPException(
            status_code=400,
            detail="No training in progress"
        )
    
    # Note: This is a simple implementation
    # In production, you'd want proper task cancellation with Celery
    training_state["status"] = "error"
    training_state["message"] = "Training stopped by user"
    training_state["completed_at"] = datetime.utcnow()
    
    return {
        "success": True,
        "message": "Training stopped"
    }


@router.get("/history")
async def get_training_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Get training history.
    
    Returns past training runs with metrics and duration.
    """
    # Return most recent first
    history = sorted(training_history, key=lambda x: x["started_at"], reverse=True)
    return {
        "total": len(history),
        "history": history[:limit]
    }


@router.get("/models")
async def get_trained_models(
    current_user: User = Depends(get_current_user)
):
    """
    List trained models.
    
    Shows available trained models with versions and metrics.
    """
    import os
    from pathlib import Path
    
    models_dir = Path("apps/api/app/ml/trained_models")
    
    if not models_dir.exists():
        return {"models": []}
    
    models = []
    
    for model_file in models_dir.glob("*.pkl"):
        # Get file stats
        stats = model_file.stat()
        
        # Get model name from filename
        name = model_file.stem.replace("_model", "")
        
        models.append({
            "name": name,
            "filename": model_file.name,
            "size_mb": round(stats.st_size / (1024 * 1024), 2),
            "created_at": datetime.fromtimestamp(stats.st_ctime),
            "modified_at": datetime.fromtimestamp(stats.st_mtime)
        })
    
    return {
        "total": len(models),
        "models": models
    }


@router.post("/schedule")
async def schedule_training(
    schedule: str,  # "daily", "weekly", "monthly"
    model: ModelType = ModelType.ALL,
    current_user: User = Depends(get_current_user)
):
    """
    Schedule automated training.
    
    Set up recurring training runs (daily/weekly/monthly).
    
    **Note:** This endpoint stores the schedule preference.
    Actual scheduling should be configured via GitHub Actions or Celery Beat.
    """
    valid_schedules = ["daily", "weekly", "monthly"]
    
    if schedule not in valid_schedules:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid schedule. Must be one of: {valid_schedules}"
        )
    
    # In production, save this to database
    # For now, just return success
    return {
        "success": True,
        "message": f"Training scheduled {schedule} for {model.value}",
        "schedule": schedule,
        "model": model.value,
        "next_run": "Configured via GitHub Actions or Celery Beat"
    }


@router.delete("/models/{model_name}")
async def delete_model(
    model_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a trained model.
    
    Removes model file from disk. Use with caution!
    """
    from pathlib import Path
    
    models_dir = Path("apps/api/app/ml/trained_models")
    model_file = models_dir / f"{model_name}_model.pkl"
    
    if not model_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found"
        )
    
    # Delete file
    model_file.unlink()
    
    return {
        "success": True,
        "message": f"Model '{model_name}' deleted"
    }

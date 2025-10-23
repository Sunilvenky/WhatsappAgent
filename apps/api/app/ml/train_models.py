"""
Complete ML Model Training Script with Progress Tracking
Run this to train all custom models on your WhatsApp data
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.ml.training_pipeline import get_training_pipeline


class TrainingOrchestrator:
    """Orchestrates the complete ML training pipeline with progress tracking."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.pipeline = get_training_pipeline()
        self.results = {}
        
    def print_header(self, text: str):
        """Print formatted header."""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)
    
    def print_step(self, step: int, total: int, text: str):
        """Print step progress."""
        print(f"\n[Step {step}/{total}] {text}")
        print("-" * 70)
    
    def print_success(self, text: str):
        """Print success message."""
        print(f"✅ {text}")
    
    def print_error(self, text: str):
        """Print error message."""
        print(f"❌ {text}")
    
    def print_info(self, text: str):
        """Print info message."""
        print(f"ℹ️  {text}")
    
    async def check_data_availability(self) -> Dict[str, Any]:
        """Check if sufficient training data is available."""
        self.print_step(1, 7, "Checking Data Availability")
        
        try:
            # Check lead scoring data
            lead_data = self.pipeline.prepare_lead_scoring_data(self.db, user_id=1)
            lead_count = len(lead_data)
            lead_ready = lead_count >= 100
            
            # Check churn data
            churn_data = self.pipeline.prepare_churn_data(self.db, user_id=1)
            churn_count = len(churn_data)
            churn_ready = churn_count >= 100
            
            # Check engagement data
            engagement_data = self.pipeline.prepare_engagement_data(self.db, user_id=1)
            engagement_count = len(engagement_data)
            engagement_ready = engagement_count >= 100
            
            # Print results
            print(f"\n📊 Data Availability:")
            print(f"   Lead Scoring:        {lead_count:>4} samples {'✅' if lead_ready else '❌ (need 100+)'}")
            print(f"   Churn Prediction:    {churn_count:>4} samples {'✅' if churn_ready else '❌ (need 100+)'}")
            print(f"   Engagement:          {engagement_count:>4} samples {'✅' if engagement_ready else '❌ (need 100+)'}")
            
            return {
                "lead_scoring": {
                    "ready": lead_ready,
                    "count": lead_count,
                    "data": lead_data if lead_ready else None
                },
                "churn_prediction": {
                    "ready": churn_ready,
                    "count": churn_count,
                    "data": churn_data if churn_ready else None
                },
                "engagement_prediction": {
                    "ready": engagement_ready,
                    "count": engagement_count,
                    "data": engagement_data if engagement_ready else None
                }
            }
            
        except Exception as e:
            self.print_error(f"Data check failed: {e}")
            return {}
    
    async def train_lead_scoring(self, data: List[Dict]) -> Dict[str, Any]:
        """Train lead scoring model."""
        self.print_step(2, 7, "Training Lead Scoring Model (XGBoost)")
        
        try:
            print("\n🎓 Training in progress...")
            print("   Algorithm: XGBoost Regressor")
            print("   Features: 24 (response, engagement, sentiment)")
            print("   Output: Score 0-100")
            
            result = self.pipeline.train_model(
                model_name="lead_scoring",
                training_data=data,
                save_model=True
            )
            
            if result.get("success"):
                metrics = result["metrics"]
                self.print_success("Lead Scoring Model Trained!")
                print(f"\n   📈 Performance Metrics:")
                print(f"      Training RMSE:    {metrics['train_rmse']:.2f}")
                print(f"      Validation RMSE:  {metrics['val_rmse']:.2f}")
                print(f"      R² Score:         {metrics['val_r2']:.3f}")
                print(f"\n   💾 Model saved: {result.get('model_path')}")
            else:
                self.print_error(f"Training failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            self.print_error(f"Lead scoring training failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def train_churn_prediction(self, data: List[Dict]) -> Dict[str, Any]:
        """Train churn prediction model."""
        self.print_step(3, 7, "Training Churn Prediction Model (Random Forest)")
        
        try:
            print("\n🎓 Training in progress...")
            print("   Algorithm: Random Forest Classifier")
            print("   Features: 32 (recency, frequency, sentiment)")
            print("   Output: Churn probability + recommendations")
            
            result = self.pipeline.train_model(
                model_name="churn_prediction",
                training_data=data,
                save_model=True
            )
            
            if result.get("success"):
                metrics = result["metrics"]
                self.print_success("Churn Prediction Model Trained!")
                print(f"\n   📈 Performance Metrics:")
                print(f"      Accuracy:   {metrics['val_accuracy']:.2%}")
                print(f"      Precision:  {metrics['val_precision']:.2%}")
                print(f"      Recall:     {metrics['val_recall']:.2%}")
                print(f"      F1 Score:   {metrics['val_f1']:.3f}")
                print(f"      ROC AUC:    {metrics['val_roc_auc']:.3f}")
                print(f"\n   💾 Model saved: {result.get('model_path')}")
            else:
                self.print_error(f"Training failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            self.print_error(f"Churn prediction training failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def train_engagement_prediction(self, data: List[Dict]) -> Dict[str, Any]:
        """Train engagement prediction model."""
        self.print_step(4, 7, "Training Engagement Prediction Model (Logistic Regression)")
        
        try:
            print("\n🎓 Training in progress...")
            print("   Algorithm: Logistic Regression")
            print("   Features: 27 (time patterns, preferences)")
            print("   Output: Engagement probability + optimal time")
            
            result = self.pipeline.train_model(
                model_name="engagement_prediction",
                training_data=data,
                save_model=True
            )
            
            if result.get("success"):
                metrics = result["metrics"]
                self.print_success("Engagement Prediction Model Trained!")
                print(f"\n   📈 Performance Metrics:")
                print(f"      Accuracy:   {metrics['val_accuracy']:.2%}")
                print(f"      Precision:  {metrics['val_precision']:.2%}")
                print(f"      Recall:     {metrics['val_recall']:.2%}")
                print(f"      F1 Score:   {metrics['val_f1']:.3f}")
                print(f"      ROC AUC:    {metrics['val_roc_auc']:.3f}")
                print(f"\n   💾 Model saved: {result.get('model_path')}")
            else:
                self.print_error(f"Training failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            self.print_error(f"Engagement prediction training failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def validate_models(self) -> Dict[str, Any]:
        """Validate all trained models."""
        self.print_step(5, 7, "Validating Trained Models")
        
        validation_results = {}
        
        # Check if model files exist
        models_dir = Path("apps/api/app/ml/trained_models")
        
        models = {
            "lead_scoring": models_dir / "lead_scoring.joblib",
            "churn_prediction": models_dir / "churn_prediction.joblib",
            "engagement_prediction": models_dir / "engagement_prediction.joblib"
        }
        
        print("\n🔍 Checking model files:")
        for name, path in models.items():
            exists = path.exists()
            validation_results[name] = exists
            status = "✅" if exists else "❌"
            print(f"   {status} {name}: {path}")
        
        return validation_results
    
    async def generate_summary(self) -> None:
        """Generate training summary."""
        self.print_step(6, 7, "Training Summary")
        
        successful = sum(1 for r in self.results.values() if r.get("success"))
        total = len(self.results)
        
        print(f"\n📊 Results:")
        print(f"   Total models:      {total}")
        print(f"   Successfully trained: {successful}")
        print(f"   Failed:            {total - successful}")
        
        if successful > 0:
            self.print_success(f"{successful}/{total} models ready for production!")
        
        if successful < total:
            self.print_error(f"{total - successful}/{total} models failed - check errors above")
    
    async def generate_next_steps(self) -> None:
        """Print next steps for user."""
        self.print_step(7, 7, "Next Steps")
        
        successful = sum(1 for r in self.results.values() if r.get("success"))
        
        if successful > 0:
            print("\n🚀 Your ML models are trained! Here's what to do next:\n")
            
            print("1️⃣  TEST THE MODELS")
            print("   Run: python -m apps.api.app.ml.test_models")
            print("   This will test predictions with sample data\n")
            
            print("2️⃣  START THE API SERVER")
            print("   Run: python -m apps.api.app.main")
            print("   Models will auto-load at startup\n")
            
            print("3️⃣  USE VIA API")
            print("   POST /api/v1/ml/models/lead-scoring/predict")
            print("   POST /api/v1/ml/models/churn-prediction/predict")
            print("   POST /api/v1/ml/models/engagement-prediction/predict\n")
            
            print("4️⃣  INTEGRATE INTO WORKFLOWS")
            print("   • Auto-score new leads")
            print("   • Daily churn check")
            print("   • Optimize campaign send times\n")
            
            print("5️⃣  MONITOR PERFORMANCE")
            print("   GET /api/v1/ml/training/status")
            print("   Track: predictions vs actual results\n")
            
            print("6️⃣  RETRAIN REGULARLY")
            print("   Schedule: Monthly retraining with new data")
            print("   Run: python -m apps.api.app.ml.train_models\n")
            
        else:
            print("\n⚠️  No models were successfully trained.\n")
            print("Possible issues:")
            print("   • Insufficient training data (need 100+ samples)")
            print("   • Database connection issues")
            print("   • Missing dependencies\n")
            print("Solutions:")
            print("   1. Generate synthetic data:")
            print("      python -m apps.api.app.ml.generate_training_data")
            print("   2. Check database connection")
            print("   3. Verify all ML libraries installed")
    
    async def run(self) -> None:
        """Run complete training pipeline."""
        try:
            self.print_header("🚀 ML MODEL TRAINING PIPELINE")
            print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Step 1: Check data
            data_status = await self.check_data_availability()
            
            if not any(v["ready"] for v in data_status.values()):
                self.print_error("No sufficient training data found!")
                print("\n💡 To generate synthetic training data, run:")
                print("   python -m apps.api.app.ml.generate_training_data")
                return
            
            # Train available models
            if data_status.get("lead_scoring", {}).get("ready"):
                result = await self.train_lead_scoring(
                    data_status["lead_scoring"]["data"]
                )
                self.results["lead_scoring"] = result
            
            if data_status.get("churn_prediction", {}).get("ready"):
                result = await self.train_churn_prediction(
                    data_status["churn_prediction"]["data"]
                )
                self.results["churn_prediction"] = result
            
            if data_status.get("engagement_prediction", {}).get("ready"):
                result = await self.train_engagement_prediction(
                    data_status["engagement_prediction"]["data"]
                )
                self.results["engagement_prediction"] = result
            
            # Step 5: Validate
            await self.validate_models()
            
            # Step 6: Summary
            await self.generate_summary()
            
            # Step 7: Next steps
            await self.generate_next_steps()
            
            self.print_header("🎉 TRAINING PIPELINE COMPLETE")
            print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            self.print_error(f"Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.db.close()


async def train_single_model(model_name: str) -> None:
    """Train a single specific model."""
    orchestrator = TrainingOrchestrator()
    
    try:
        orchestrator.print_header(f"🚀 TRAINING {model_name.upper().replace('_', ' ')} MODEL")
        
        # Check data
        data_status = await orchestrator.check_data_availability()
        
        if not data_status.get(model_name, {}).get("ready"):
            orchestrator.print_error(f"Insufficient data for {model_name}")
            return
        
        # Train specific model
        if model_name == "lead_scoring":
            result = await orchestrator.train_lead_scoring(
                data_status["lead_scoring"]["data"]
            )
        elif model_name == "churn_prediction":
            result = await orchestrator.train_churn_prediction(
                data_status["churn_prediction"]["data"]
            )
        elif model_name == "engagement_prediction":
            result = await orchestrator.train_engagement_prediction(
                data_status["engagement_prediction"]["data"]
            )
        else:
            orchestrator.print_error(f"Unknown model: {model_name}")
            return
        
        orchestrator.results[model_name] = result
        
        orchestrator.print_header("🎉 TRAINING COMPLETE")
        
    finally:
        orchestrator.db.close()


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
        if model_name not in ["lead_scoring", "churn_prediction", "engagement_prediction"]:
            print("❌ Invalid model name!")
            print("\nUsage:")
            print("  python -m apps.api.app.ml.train_models                    # Train all")
            print("  python -m apps.api.app.ml.train_models lead_scoring       # Train one")
            print("  python -m apps.api.app.ml.train_models churn_prediction")
            print("  python -m apps.api.app.ml.train_models engagement_prediction")
            sys.exit(1)
        
        asyncio.run(train_single_model(model_name))
    else:
        orchestrator = TrainingOrchestrator()
        asyncio.run(orchestrator.run())


if __name__ == "__main__":
    main()

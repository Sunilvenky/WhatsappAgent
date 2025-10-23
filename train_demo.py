"""
Simplified ML Training Demo (No Database Required)
Demonstrates the ML training system with sample data
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBRegressor
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, r2_score
import joblib
from pathlib import Path
import time


class SimpleMLTrainingDemo:
    """Simple ML training demonstration without database."""
    
    def __init__(self):
        self.models_dir = Path("apps/api/app/ml/trained_models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def print_header(self, title: str):
        """Print section header."""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def generate_lead_scoring_data(self, n_samples: int = 120):
        """Generate synthetic lead scoring data."""
        print("\n📊 Generating lead scoring data...")
        
        np.random.seed(42)
        
        # Generate features
        data = {
            'response_rate': np.random.uniform(0, 1, n_samples),
            'message_count': np.random.randint(1, 50, n_samples),
            'avg_response_time': np.random.uniform(1, 3600, n_samples),
            'sentiment_score': np.random.uniform(-1, 1, n_samples),
            'engagement_score': np.random.uniform(0, 100, n_samples),
            'conversation_length': np.random.randint(1, 20, n_samples),
            'days_since_contact': np.random.randint(1, 90, n_samples),
            'opened_messages': np.random.randint(0, 30, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate target scores based on features
        scores = (
            df['response_rate'] * 30 +
            df['engagement_score'] * 0.5 +
            df['sentiment_score'] * 20 +
            (50 / (df['avg_response_time'] / 60 + 1)) +
            np.random.normal(0, 5, n_samples)
        )
        scores = np.clip(scores, 0, 100)
        
        print(f"   ✅ Generated {n_samples} lead samples")
        print(f"   📈 Score range: {scores.min():.1f} - {scores.max():.1f}")
        
        return df, scores
    
    def generate_churn_data(self, n_samples: int = 150):
        """Generate synthetic churn prediction data."""
        print("\n📊 Generating churn prediction data...")
        
        np.random.seed(43)
        
        # Generate features
        data = {
            'days_since_last_message': np.random.randint(0, 90, n_samples),
            'total_messages': np.random.randint(1, 100, n_samples),
            'avg_sentiment': np.random.uniform(-1, 1, n_samples),
            'message_frequency': np.random.uniform(0, 10, n_samples),
            'negative_replies': np.random.randint(0, 20, n_samples),
            'unsubscribe_mentions': np.random.randint(0, 5, n_samples),
            'engagement_trend': np.random.uniform(-1, 1, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate churn labels based on features
        churn_probability = (
            (df['days_since_last_message'] / 90) * 0.3 +
            (1 - df['avg_sentiment']) * 0.2 +
            (df['negative_replies'] / 20) * 0.2 +
            (df['unsubscribe_mentions'] / 5) * 0.2 +
            (1 - df['engagement_trend']) * 0.1
        )
        churned = (churn_probability + np.random.normal(0, 0.1, n_samples)) > 0.5
        
        print(f"   ✅ Generated {n_samples} contact samples")
        print(f"   📈 Churn rate: {churned.mean():.1%}")
        
        return df, churned.astype(int)
    
    def generate_engagement_data(self, n_samples: int = 150):
        """Generate synthetic engagement prediction data."""
        print("\n📊 Generating engagement prediction data...")
        
        np.random.seed(44)
        
        # Generate features
        data = {
            'hour_of_day': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'message_length': np.random.randint(10, 500, n_samples),
            'has_emoji': np.random.randint(0, 2, n_samples),
            'sentiment': np.random.uniform(-1, 1, n_samples),
            'past_engagement_rate': np.random.uniform(0, 1, n_samples),
            'is_weekend': np.random.randint(0, 2, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate engagement based on patterns
        engagement_score = (
            (df['past_engagement_rate']) * 0.4 +
            ((df['hour_of_day'] >= 10) & (df['hour_of_day'] <= 16)).astype(int) * 0.2 +
            (df['sentiment'] > 0).astype(int) * 0.2 +
            (df['has_emoji']) * 0.1 +
            (df['message_length'] < 200).astype(int) * 0.1
        )
        engaged = (engagement_score + np.random.normal(0, 0.15, n_samples)) > 0.5
        
        print(f"   ✅ Generated {n_samples} message samples")
        print(f"   📈 Engagement rate: {engaged.mean():.1%}")
        
        return df, engaged.astype(int)
    
    def train_lead_scoring_model(self):
        """Train lead scoring model."""
        self.print_header("🎯 TRAINING LEAD SCORING MODEL")
        
        # Generate data
        X, y = self.generate_lead_scoring_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\n📊 Data split:")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        print(f"   Features: {len(X.columns)}")
        
        # Train model
        print("\n🔧 Training XGBoost model...")
        start_time = time.time()
        
        model = XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        training_time = time.time() - start_time
        
        # Evaluate
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"✅ Training complete! ({training_time:.1f}s)")
        print(f"\n📈 Model Performance:")
        print(f"   Mean Absolute Error: {mae:.2f}")
        print(f"   R² Score: {r2:.3f}")
        
        # Save model
        model_path = self.models_dir / "lead_scoring_model.pkl"
        joblib.dump(model, model_path)
        print(f"   💾 Model saved: {model_path}")
        
        return {
            'mae': mae,
            'r2': r2,
            'training_time': training_time
        }
    
    def train_churn_model(self):
        """Train churn prediction model."""
        self.print_header("⚠️  TRAINING CHURN PREDICTION MODEL")
        
        # Generate data
        X, y = self.generate_churn_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\n📊 Data split:")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        print(f"   Features: {len(X.columns)}")
        
        # Train model
        print("\n🔧 Training Random Forest model...")
        start_time = time.time()
        
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        training_time = time.time() - start_time
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"✅ Training complete! ({training_time:.1f}s)")
        print(f"\n📈 Model Performance:")
        print(f"   Accuracy: {accuracy:.1%}")
        print(f"   F1 Score: {f1:.3f}")
        
        # Save model
        model_path = self.models_dir / "churn_model.pkl"
        joblib.dump(model, model_path)
        print(f"   💾 Model saved: {model_path}")
        
        return {
            'accuracy': accuracy,
            'f1': f1,
            'training_time': training_time
        }
    
    def train_engagement_model(self):
        """Train engagement prediction model."""
        self.print_header("📊 TRAINING ENGAGEMENT PREDICTION MODEL")
        
        # Generate data
        X, y = self.generate_engagement_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\n📊 Data split:")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        print(f"   Features: {len(X.columns)}")
        
        # Train model
        print("\n🔧 Training Logistic Regression model...")
        start_time = time.time()
        
        model = LogisticRegression(
            max_iter=1000,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        training_time = time.time() - start_time
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"✅ Training complete! ({training_time:.1f}s)")
        print(f"\n📈 Model Performance:")
        print(f"   Accuracy: {accuracy:.1%}")
        print(f"   F1 Score: {f1:.3f}")
        
        # Save model
        model_path = self.models_dir / "engagement_model.pkl"
        joblib.dump(model, model_path)
        print(f"   💾 Model saved: {model_path}")
        
        return {
            'accuracy': accuracy,
            'f1': f1,
            'training_time': training_time
        }
    
    def train_all(self):
        """Train all models."""
        print("\n" + "=" * 70)
        print("  🤖 ML MODEL TRAINING PIPELINE - DEMO")
        print("=" * 70)
        print("\nTraining 3 ML models with synthetic data...\n")
        
        # Train all models
        results = {}
        results['lead_scoring'] = self.train_lead_scoring_model()
        results['churn'] = self.train_churn_model()
        results['engagement'] = self.train_engagement_model()
        
        # Summary
        self.print_header("✅ TRAINING COMPLETE")
        
        total_time = sum(r['training_time'] for r in results.values())
        
        print(f"\n📊 Summary:")
        print(f"   Total training time: {total_time:.1f}s")
        print(f"   Models trained: 3/3")
        
        print(f"\n📈 Performance:")
        print(f"   Lead Scoring:")
        print(f"      MAE: {results['lead_scoring']['mae']:.2f}")
        print(f"      R²: {results['lead_scoring']['r2']:.3f}")
        
        print(f"   Churn Prediction:")
        print(f"      Accuracy: {results['churn']['accuracy']:.1%}")
        print(f"      F1: {results['churn']['f1']:.3f}")
        
        print(f"   Engagement Prediction:")
        print(f"      Accuracy: {results['engagement']['accuracy']:.1%}")
        print(f"      F1: {results['engagement']['f1']:.3f}")
        
        print(f"\n💾 Models saved to: {self.models_dir}")
        
        print(f"\n🎉 All models trained successfully!")
        print(f"\n💡 Next steps:")
        print(f"   • Models are ready for predictions")
        print(f"   • Check {self.models_dir} for .pkl files")
        print(f"   • Use models in your WhatsApp Agent platform")


if __name__ == "__main__":
    trainer = SimpleMLTrainingDemo()
    trainer.train_all()

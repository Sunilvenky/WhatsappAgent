"""
Test trained ML models with sample predictions.
Validates that models work correctly before production use.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.ml.models.lead_scoring import LeadScoringModel
from app.ml.models.churn_prediction import ChurnPredictionModel
from app.ml.models.engagement_prediction import EngagementPredictionModel


class ModelTester:
    """Test trained ML models."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def print_section(self, title: str):
        """Print section header."""
        print(f"\n{'=' * 70}")
        print(f"  {title}")
        print("=" * 70)
    
    async def test_lead_scoring(self) -> Dict[str, Any]:
        """Test lead scoring model."""
        self.print_section("🎯 TESTING LEAD SCORING MODEL")
        
        try:
            model = LeadScoringModel()
            
            # Load model
            print("\n📥 Loading model...")
            model.load()
            print("✅ Model loaded successfully")
            
            # Get sample leads
            print("\n📊 Fetching sample leads...")
            from app.crud import lead as lead_crud
            leads = lead_crud.get_leads(self.db, skip=0, limit=5)
            
            if not leads:
                print("⚠️  No leads found in database. Generate data first.")
                return {"success": False, "reason": "no_data"}
            
            print(f"✅ Found {len(leads)} leads to test")
            
            # Predict scores
            print("\n🔮 Making predictions...")
            results = []
            
            for i, lead in enumerate(leads, 1):
                print(f"\n   Lead #{i} (ID: {lead.id}):")
                
                # Predict
                result = await model.predict_lead_score(self.db, lead.id)
                
                if result.get("success"):
                    print(f"      Score: {result['score']:.1f}/100")
                    print(f"      Quality: {result['quality_tier']}")
                    print(f"      Recommendation: {result['recommendation']}")
                    results.append(result)
                else:
                    print(f"      ❌ Prediction failed: {result.get('error')}")
            
            # Summary
            if results:
                avg_score = sum(r['score'] for r in results) / len(results)
                print(f"\n📈 Results:")
                print(f"   Average Score: {avg_score:.1f}/100")
                print(f"   Predictions: {len(results)}/{len(leads)}")
                print(f"   ✅ Lead scoring model working correctly")
                
                return {
                    "success": True,
                    "predictions": len(results),
                    "average_score": avg_score
                }
            else:
                print("\n❌ All predictions failed")
                return {"success": False, "reason": "prediction_failed"}
                
        except FileNotFoundError:
            print("\n❌ Model not found. Train models first:")
            print("   python -m apps.api.app.ml.train_models lead_scoring")
            return {"success": False, "reason": "model_not_found"}
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def test_churn_prediction(self) -> Dict[str, Any]:
        """Test churn prediction model."""
        self.print_section("⚠️  TESTING CHURN PREDICTION MODEL")
        
        try:
            model = ChurnPredictionModel()
            
            # Load model
            print("\n📥 Loading model...")
            model.load()
            print("✅ Model loaded successfully")
            
            # Get sample contacts
            print("\n📊 Fetching sample contacts...")
            from app.crud import contact as contact_crud
            contacts = contact_crud.get_contacts(self.db, skip=0, limit=5)
            
            if not contacts:
                print("⚠️  No contacts found in database. Generate data first.")
                return {"success": False, "reason": "no_data"}
            
            print(f"✅ Found {len(contacts)} contacts to test")
            
            # Predict churn
            print("\n🔮 Making predictions...")
            results = []
            
            for i, contact in enumerate(contacts, 1):
                print(f"\n   Contact #{i} (ID: {contact.id}, Name: {contact.name}):")
                
                # Predict
                result = await model.predict_churn(self.db, contact.id)
                
                if result.get("success"):
                    print(f"      Churn Probability: {result['churn_probability']:.1%}")
                    print(f"      Risk Level: {result['risk_level']}")
                    print(f"      Recommendations: {len(result['recommendations'])} actions")
                    results.append(result)
                else:
                    print(f"      ❌ Prediction failed: {result.get('error')}")
            
            # Summary
            if results:
                avg_risk = sum(r['churn_probability'] for r in results) / len(results)
                high_risk = sum(1 for r in results if r['risk_level'] == 'high')
                
                print(f"\n📈 Results:")
                print(f"   Average Churn Risk: {avg_risk:.1%}")
                print(f"   High Risk Contacts: {high_risk}/{len(results)}")
                print(f"   Predictions: {len(results)}/{len(contacts)}")
                print(f"   ✅ Churn prediction model working correctly")
                
                return {
                    "success": True,
                    "predictions": len(results),
                    "average_risk": avg_risk,
                    "high_risk_count": high_risk
                }
            else:
                print("\n❌ All predictions failed")
                return {"success": False, "reason": "prediction_failed"}
                
        except FileNotFoundError:
            print("\n❌ Model not found. Train models first:")
            print("   python -m apps.api.app.ml.train_models churn")
            return {"success": False, "reason": "model_not_found"}
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def test_engagement_prediction(self) -> Dict[str, Any]:
        """Test engagement prediction model."""
        self.print_section("📊 TESTING ENGAGEMENT PREDICTION MODEL")
        
        try:
            model = EngagementPredictionModel()
            
            # Load model
            print("\n📥 Loading model...")
            model.load()
            print("✅ Model loaded successfully")
            
            # Get sample contacts
            print("\n📊 Fetching sample contacts...")
            from app.crud import contact as contact_crud
            contacts = contact_crud.get_contacts(self.db, skip=0, limit=5)
            
            if not contacts:
                print("⚠️  No contacts found in database. Generate data first.")
                return {"success": False, "reason": "no_data"}
            
            print(f"✅ Found {len(contacts)} contacts to test")
            
            # Predict engagement
            print("\n🔮 Making predictions...")
            results = []
            
            for i, contact in enumerate(contacts, 1):
                print(f"\n   Contact #{i} (ID: {contact.id}, Name: {contact.name}):")
                
                # Predict
                result = await model.predict_engagement(
                    self.db,
                    contact.id,
                    "Hi! We have a special offer for you."
                )
                
                if result.get("success"):
                    print(f"      Engagement Probability: {result['engagement_probability']:.1%}")
                    print(f"      Optimal Send Time: {result['optimal_send_time']}")
                    print(f"      Best Day: {result['best_day']}")
                    results.append(result)
                else:
                    print(f"      ❌ Prediction failed: {result.get('error')}")
            
            # Summary
            if results:
                avg_engagement = sum(r['engagement_probability'] for r in results) / len(results)
                high_engagement = sum(1 for r in results if r['engagement_probability'] > 0.7)
                
                print(f"\n📈 Results:")
                print(f"   Average Engagement: {avg_engagement:.1%}")
                print(f"   High Engagement Contacts: {high_engagement}/{len(results)}")
                print(f"   Predictions: {len(results)}/{len(contacts)}")
                print(f"   ✅ Engagement prediction model working correctly")
                
                return {
                    "success": True,
                    "predictions": len(results),
                    "average_engagement": avg_engagement,
                    "high_engagement_count": high_engagement
                }
            else:
                print("\n❌ All predictions failed")
                return {"success": False, "reason": "prediction_failed"}
                
        except FileNotFoundError:
            print("\n❌ Model not found. Train models first:")
            print("   python -m apps.api.app.ml.train_models engagement")
            return {"success": False, "reason": "model_not_found"}
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def test_all(self) -> Dict[str, Any]:
        """Test all models."""
        print("\n" + "=" * 70)
        print("  🧪 ML MODEL TESTING SUITE")
        print("=" * 70)
        print("\nTesting all trained ML models with sample predictions...")
        
        results = {
            "lead_scoring": await self.test_lead_scoring(),
            "churn_prediction": await self.test_churn_prediction(),
            "engagement_prediction": await self.test_engagement_prediction()
        }
        
        # Final summary
        print("\n" + "=" * 70)
        print("  📋 TESTING SUMMARY")
        print("=" * 70)
        
        successes = sum(1 for r in results.values() if r.get("success"))
        total = len(results)
        
        print(f"\n✅ Passed: {successes}/{total} models")
        
        for model_name, result in results.items():
            status = "✅ PASS" if result.get("success") else "❌ FAIL"
            reason = f" ({result.get('reason', result.get('error', 'unknown'))})" if not result.get("success") else ""
            print(f"   {status} - {model_name}{reason}")
        
        if successes == total:
            print("\n🎉 All models working correctly!")
            print("\n💡 Next Steps:")
            print("   1. Deploy models to production")
            print("   2. Set up automated retraining (weekly recommended)")
            print("   3. Monitor prediction accuracy")
        else:
            print("\n⚠️  Some models failed. Check errors above.")
            print("\n💡 Troubleshooting:")
            print("   • If 'model_not_found': Train models first")
            print("   • If 'no_data': Generate training data first")
            print("   • If 'prediction_failed': Check model quality")
        
        return {
            "success": successes == total,
            "passed": successes,
            "total": total,
            "results": results
        }


async def main():
    """Main entry point."""
    db = SessionLocal()
    
    try:
        tester = ModelTester(db)
        result = await tester.test_all()
        
        if not result.get("success"):
            exit(1)
            
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())

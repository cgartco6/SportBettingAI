import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from .base_agent import BaseAgent
from config import Config
from utils.data_utils import calculate_accuracy

class QAAgent(BaseAgent):
    def execute(self):
        print(f"[{self.agent_id}] Performing quality assurance")
        review_type = self.task_spec.get("review_type", "cross_validation")
        
        if review_type == "cross_validation":
            result = self.cross_validate_model()
        elif review_type == "prediction_validation":
            result = self.validate_predictions()
        elif review_type == "result_verification":
            result = self.verify_results()
        else:
            result = {"status": "error", "message": "Invalid review type"}
        
        # Handle issues found
        if result.get("issues_found", 0) > 0:
            self.handle_issues(result)
        
        return result
    
    def cross_validate_model(self):
        """Perform cross-validation on the model"""
        print("Performing cross-validation")
        model = self.conductor.model_registry.get("dc_btts_predictor")
        if not model:
            return {"status": "error", "message": "No model available for validation"}
        
        # Get training data
        data = self.get_training_data()
        if data is None:
            return {"status": "error", "message": "No training data available"}
        
        # Prepare for cross-validation
        X = data.drop(columns=[Config.TARGET])
        y = data[Config.TARGET]
        
        kf = KFold(n_splits=5, shuffle=True)
        accuracies = []
        
        # Perform k-fold cross validation
        for train_index, test_index in kf.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            # Train and validate
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            accuracy = calculate_accuracy(y_test, preds)
            accuracies.append(accuracy)
        
        # Calculate average accuracy
        avg_accuracy = np.mean(accuracies)
        print(f"Cross-validation accuracy: {avg_accuracy:.2%}")
        
        # Trigger retraining if below threshold
        if avg_accuracy < Config.PERFORMANCE_THRESHOLD:
            print("Accuracy below threshold - triggering retraining")
            retrain_agent_id = self.create_sub_agent(
                "model_trainer",
                {
                    "model_type": "hybrid",
                    "target": "dc_btts",
                    "retrain": True,
                    "validation_accuracy": avg_accuracy
                }
            )
            return {
                "status": "retraining_triggered",
                "accuracy": avg_accuracy,
                "next_agent": retrain_agent_id
            }
        
        return {
            "status": "success",
            "accuracy": avg_accuracy,
            "message": f"Cross-validation completed with {avg_accuracy:.2%} accuracy"
        }
    
    def validate_predictions(self):
        """Validate the prediction engine's output"""
        print("Validating predictions")
        predictions = self.task_spec.get("predictions", pd.DataFrame())
        
        if predictions.empty:
            return {"status": "error", "message": "No predictions to validate"}
        
        # Check for required columns
        required_cols = ["match_id", "home_team", "away_team", "prediction", "confidence"]
        missing_cols = [col for col in required_cols if col not in predictions.columns]
        if missing_cols:
            return {
                "status": "error",
                "message": f"Missing columns in predictions: {', '.join(missing_cols)}"
            }
        
        # Check confidence distribution
        high_confidence = predictions[predictions["confidence"] >= 0.7]
        medium_confidence = predictions[(predictions["confidence"] >= 0.6) & (predictions["confidence"] < 0.7)]
        low_confidence = predictions[predictions["confidence"] < 0.6]
        
        # Check if too many low confidence predictions
        if len(low_confidence) / len(predictions) > 0.5:
            print("Too many low-confidence predictions - triggering model review")
            review_agent_id = self.create_sub_agent(
                "qa_agent",
                {"review_type": "cross_validation"}
            )
            return {
                "status": "model_review_triggered",
                "next_agent": review_agent_id
            }
        
        # Create value identifier agent
        value_agent_id = self.create_sub_agent(
            "value_identifier",
            {
                "threshold": Config.VALUE_THRESHOLD,
                "predictions": predictions
            }
        )
        
        return {
            "status": "success",
            "high_confidence": len(high_confidence),
            "medium_confidence": len(medium_confidence),
            "low_confidence": len(low_confidence),
            "next_agent": value_agent_id
        }
    
    def verify_results(self):
        """Verify actual results against predictions"""
        print("Verifying results")
        # Get unverified predictions
        unverified = [p for p in self.conductor.prediction_log if not p["verified"]]
        
        if not unverified:
            return {"status": "success", "message": "No unverified predictions"}
        
        # Get actual results (in production, this would be from a data source)
        actual_results = self.get_actual_results()
        
        # Verify predictions
        verified = []
        for prediction in unverified:
            match_result = actual_results.get(prediction["match_id"])
            if match_result:
                prediction["actual"] = match_result["result"]
                prediction["btss"] = match_result["both_scored"]
                prediction["verified"] = True
                
                # Determine if prediction was correct
                if match_result["result"] in ["home_win", "away_win", "draw"] and match_result["both_scored"]:
                    prediction["correct"] = prediction["prediction"]
                else:
                    prediction["correct"] = not prediction["prediction"]
                
                # Log performance
                self.log_performance(
                    "win" if prediction["correct"] else "loss",
                    prediction["confidence"]
                )
                verified.append(prediction)
        
        # Update performance metrics
        if verified:
            wins = sum(1 for p in verified if p["correct"])
            total = len(verified)
            win_rate = wins / total
            
            # Create performance report
            report_agent_id = self.create_sub_agent(
                "reporting_agent",
                {"platforms": ["dashboard"], "report_type": "performance_update"}
            )
            
            return {
                "status": "success",
                "verified_count": len(verified),
                "win_rate": win_rate,
                "next_agent": report_agent_id
            }
        else:
            return {"status": "success", "message": "No results available for verification"}
    
    def get_training_data(self):
        """Retrieve training data"""
        # In production, this would come from the data pipeline
        try:
            return pd.read_csv(f"{Config.DATA_PATH}training_data.csv")
        except:
            return None
    
    def get_actual_results(self):
        """Retrieve actual match results (demo implementation)"""
        # In production, this would be from a sports data API
        return {
            101: {"result": "home_win", "both_scored": True},
            102: {"result": "draw", "both_scored": False},
            103: {"result": "away_win", "both_scored": True}
        }
    
    def handle_issues(self, result):
        """Handle issues found during QA"""
        issues = result.get("issues_found", 0)
        issue_type = result.get("issue_type")
        
        if issue_type == "data_quality":
            print(f"Found {issues} data quality issues - triggering data repair")
            self.create_sub_agent(
                "data_repair_agent",
                {"issue_details": result["issues"]}
            )
        elif issue_type == "model_performance":
            print("Model performance issues - triggering retraining")
            self.create_sub_agent(
                "model_trainer",
                {
                    "model_type": "hybrid",
                    "target": "dc_btts",
                    "retrain": True,
                    "reason": "QA performance issues"
                }
            )

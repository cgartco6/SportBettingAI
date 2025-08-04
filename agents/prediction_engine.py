import pandas as pd
import numpy as np
from .base_agent import BaseAgent
from config import Config
from utils.data_utils import preprocess_prediction_data

class PredictionEngineAgent(BaseAgent):
    def execute(self):
        print(f"[{self.agent_id}] Generating predictions")
        min_confidence = self.task_spec.get("min_confidence", 0.65)
        
        # Get trained model
        model = self.conductor.model_registry.get("dc_btts_predictor")
        if not model:
            print("No model found - creating model training sub-agent")
            trainer_id = self.create_sub_agent(
                "model_trainer",
                {"model_type": "hybrid", "target": "dc_btts"}
            )
            return {"status": "pending", "next_agent": trainer_id}
        
        # Get latest data
        raw_data = self.get_latest_data()
        
        # Preprocess data
        prediction_data = preprocess_prediction_data(raw_data)
        
        # Generate predictions
        predictions = self.generate_predictions(model, prediction_data, min_confidence)
        
        # Store predictions
        self.conductor.current_predictions = predictions
        
        # Create QA sub-agent
        qa_agent_id = self.create_sub_agent(
            "qa_agent",
            {
                "review_type": "prediction_validation",
                "predictions": predictions
            }
        )
        
        return {
            "status": "success", 
            "predictions": predictions,
            "next_agent": qa_agent_id
        }
    
    def get_latest_data(self):
        """Retrieve the most recent processed data"""
        # In a real system, this would come from the data pipeline
        # For demo purposes, we'll load from a file
        try:
            return pd.read_csv(f"{Config.DATA_PATH}latest_processed.csv")
        except:
            # If no data available, create data collection agent
            print("No data available - triggering data collection")
            collector_id = self.create_sub_agent(
                "data_collector",
                {"sources": Config.BOOKMAKERS}
            )
            return None
    
    def generate_predictions(self, model, data, min_confidence):
        """Generate predictions using the trained model"""
        if data is None or data.empty:
            return pd.DataFrame()
        
        # Make predictions
        features = data[Config.REQUIRED_FEATURES]
        probabilities = model.predict_proba(features)[:, 1]
        
        # Create prediction results
        predictions = data[["match_id", "home_team", "away_team"]].copy()
        predictions["prediction_prob"] = probabilities
        predictions["prediction"] = probabilities >= min_confidence
        predictions["confidence"] = np.where(
            probabilities >= min_confidence,
            probabilities,
            1 - probabilities
        )
        
        # Add bookmaker odds
        bookmaker_odds = self.get_bookmaker_odds()
        predictions = predictions.merge(
            bookmaker_odds,
            on="match_id",
            how="left"
        )
        
        # Calculate value score
        predictions["implied_prob"] = 1 / predictions["bookmaker_odds"]
        predictions["value_score"] = predictions["prediction_prob"] - predictions["implied_prob"]
        
        return predictions
    
    def get_bookmaker_odds(self):
        """Get latest odds from bookmakers"""
        # In production, this would be real-time API calls
        # For demo, we'll use sample data
        return pd.DataFrame({
            "match_id": [101, 102, 103],
            "bookmaker_odds": [2.5, 3.2, 2.8]
        })
    
    def log_prediction(self, match_id, prediction, confidence):
        """Log prediction for future verification"""
        self.conductor.prediction_log.append({
            "timestamp": pd.Timestamp.now(),
            "match_id": match_id,
            "prediction": prediction,
            "confidence": confidence,
            "verified": False
        })

import numpy as np
import joblib
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from .base_agent import BaseAgent
from models.hybrid_model import HybridModel
from config import Config

class ModelTrainerAgent(BaseAgent):
    def execute(self):
        print(f"[{self.agent_id}] Training model")
        # Get processed data from feature engineer
        all_data = self.conductor.task_history[-1]["result"]["data"]
        combined_data = pd.concat(all_data, ignore_index=True)
        
        # Train model
        model = HybridModel()
        model.train(combined_data, target="dc_btts")
        
        # Validate model
        accuracy = model.validate()
        print(f"Model accuracy: {accuracy:.2%}")
        
        # Self-healing if performance is low
        if accuracy < Config.PERFORMANCE_THRESHOLD:
            print("Initiating adaptive retraining...")
            retrain_agent_id = self.create_sub_agent(
                "model_retrainer",
                {
                    "model_type": "ensemble",
                    "data": combined_data,
                    "previous_accuracy": accuracy
                }
            )
        
        # Register model
        self.conductor.model_registry["dc_btts_predictor"] = model
        
        # Create prediction agent
        prediction_agent_id = self.create_sub_agent(
            "prediction_engine",
            {"min_confidence": 0.7}
        )
        
        return {
            "status": "success", 
            "accuracy": accuracy,
            "next_agent": prediction_agent_id
        }

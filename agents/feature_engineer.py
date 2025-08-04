import pandas as pd
import numpy as np
from .base_agent import BaseAgent
from config import Config
from utils.data_utils import calculate_form_index, calculate_injury_impact

class FeatureEngineerAgent(BaseAgent):
    def execute(self):
        print(f"[{self.agent_id}] Engineering features")
        # Get data from previous agent
        raw_data = self.conductor.task_history[-1]["result"]["data"]
        
        # Process features
        processed_data = []
        for bookmaker_data in raw_data:
            df = self.process_features(bookmaker_data)
            processed_data.append(df)
        
        # Create model training sub-agent
        model_agent_id = self.create_sub_agent(
            "model_trainer",
            {
                "model_type": "hybrid",
                "target": "dc_btts",
                "data": processed_data
            }
        )
        
        return {
            "status": "success", 
            "feature_count": len(Config.REQUIRED_FEATURES),
            "next_agent": model_agent_id
        }
    
    def process_features(self, df):
        # Calculate complex features
        df["player_form"] = df.apply(lambda x: calculate_form_index(x['home_players'], x['away_players']), axis=1)
        df["team_form"] = df.apply(lambda x: np.mean([x['home_form'], x['away_form']]), axis=1)
        df["coach_form"] = df.apply(lambda x: (x['home_coach_rating'] + x['away_coach_rating']) / 2, axis=1)
        df["injury_impact"] = df.apply(lambda x: calculate_injury_impact(x['home_injuries'], x['away_injuries']), axis=1)
        df["home_advantage"] = df["home_win_pct"] - df["away_win_pct"]
        
        # Weather impact
        df["weather_impact"] = np.where(
            df["weather_condition"].isin(["Rain", "Snow"]), 
            0.8, 
            1.0
        )
        
        # Pitch condition
        df["pitch_quality"] = df["pitch_rating"].apply(
            lambda x: 1.0 if x > 7 else 0.7 if x > 5 else 0.5
        )
        
        # Select required features
        return df[Config.REQUIRED_FEATURES + ["match_id", "home_team", "away_team"]]

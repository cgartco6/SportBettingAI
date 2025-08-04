import pandas as pd
from .base_agent import BaseAgent
from config import Config

class ValueIdentifierAgent(BaseAgent):
    def execute(self):
        print(f"[{self.agent_id}] Identifying value bets")
        # Get predictions from previous agent
        predictions = self.conductor.task_history[-1]["result"]["predictions"]
        
        # Calculate value scores
        value_bets = []
        for _, row in predictions.iterrows():
            implied_prob = 1 / row['bookmaker_odds']
            value_score = row['prediction_prob'] - implied_prob
            
            if abs(value_score) > Config.VALUE_THRESHOLD:
                value_bets.append({
                    "match_id": row['match_id'],
                    "home_team": row['home_team'],
                    "away_team": row['away_team'],
                    "prediction": row['prediction'],
                    "confidence": row['confidence'],
                    "bookmaker_odds": row['bookmaker_odds'],
                    "value_score": value_score,
                    "bet_type": "UNDERVALUE" if value_score > 0 else "OVERVALUE"
                })
        
        # Create sub-agents for deep analysis
        if value_bets:
            deep_analysis_agent = self.create_sub_agent(
                "value_analyzer",
                {"bets": value_bets, "depth": "advanced"}
            )
        
        # Create reporting agent
        reporting_agent_id = self.create_sub_agent(
            "reporting_agent",
            {"platforms": ["telegram", "dashboard"]}
        )
        
        return {
            "status": "success", 
            "value_bets": value_bets,
            "next_agent": reporting_agent_id
        }

import requests
import pandas as pd
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from utils.api_clients import HollywoodbetsClient, BetwayClient
from config import Config

class DataCollectorAgent(BaseAgent):
    def execute(self):
        print(f"[{self.agent_id}] Collecting data from {Config.BOOKMAKERS}")
        all_data = []
        
        # Collect from primary sources
        for bookmaker in Config.BOOKMAKERS:
            try:
                if bookmaker == "Hollywoodbets":
                    client = HollywoodbetsClient(Config.HOLLYWOODBETS_API_KEY)
                else:
                    client = BetwayClient(Config.BETWAY_API_KEY)
                
                data = client.get_dc_btts_odds()
                all_data.append(data)
                self.log_success(bookmaker, len(data))
                self.cost += 0.01 * len(data)  # Simulate API cost
            except Exception as e:
                print(f"Error collecting {bookmaker} data: {str(e)}")
                self.handle_error(bookmaker, str(e))
                # Self-healing: Try historical data
                historical_data = self.get_historical_data(bookmaker)
                if historical_data is not None:
                    all_data.append(historical_data)
        
        # Create feature engineering sub-agent
        feature_agent_id = self.create_sub_agent(
            "feature_engineer",
            {"features": Config.REQUIRED_FEATURES}
        )
        
        # Store in long-term memory
        self.long_term_memory.extend(all_data)
        return {
            "status": "success", 
            "data_points": sum(len(d) for d in all_data),
            "next_agent": feature_agent_id
        }
    
    def get_historical_data(self, bookmaker):
        """Fallback to historical data when API fails"""
        try:
            # In production, would fetch from database
            print(f"Using historical data for {bookmaker}")
            return pd.read_csv(f"{Config.DATA_PATH}{bookmaker.lower()}_historical.csv")
        except:
            print(f"No historical data available for {bookmaker}")
            return None
    
    def log_success(self, source, count):
        print(f"Collected {count} records from {source}")
        
    def handle_error(self, source, error):
        print(f"Error collecting from {source}: {error}")
        # Create self-healing sub-agent
        self.create_sub_agent(
            "data_repair_agent",
            {"source": source, "error": error}
        )

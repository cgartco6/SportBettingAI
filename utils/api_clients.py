import requests
import pandas as pd
from config import Config

class HollywoodbetsClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.hollywoodbets.com/v1"
        
    def get_dc_btts_odds(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(
            f"{self.base_url}/events?market=DC_BTTS",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        events = response.json()["events"]
        return pd.DataFrame([{
            "match_id": e["id"],
            "home_team": e["homeTeam"],
            "away_team": e["awayTeam"],
            "bookmaker": "Hollywoodbets",
            "dc_btts_odds": e["markets"]["DC_BTTS"]["odds"]
        } for e in events])

class BetwayClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.betway.com/sports"
        
    def get_dc_btts_odds(self):
        headers = {"x-api-key": self.api_key}
        response = requests.get(
            f"{self.base_url}/events?market=double_chance_btts",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        events = response.json()["data"]
        return pd.DataFrame([{
            "match_id": e["id"],
            "home_team": e["competitors"][0]["name"],
            "away_team": e["competitors"][1]["name"],
            "bookmaker": "Betway",
            "dc_btts_odds": e["odds"]["double_chance_btts"]
        } for e in events])

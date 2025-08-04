import os

class Config:
    # Core settings
    INITIAL_BUDGET = float(os.getenv("INITIAL_BUDGET", 10000))
    PERFORMANCE_THRESHOLD = 0.65  # Minimum accuracy before retraining
    VALUE_THRESHOLD = 0.15  # Minimum value score to consider
    
    # API credentials
    HOLLYWOODBETS_API_KEY = os.getenv("HOLLYWOODBETS_API_KEY")
    BETWAY_API_KEY = os.getenv("BETWAY_API_KEY")
    
    # Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Paths
    DATA_PATH = "data/"
    MODEL_PATH = "models/"
    
    # Feature configuration
    REQUIRED_FEATURES = [
        "player_form", 
        "team_form", 
        "coach_form", 
        "injuries", 
        "home_away", 
        "transfers", 
        "weather", 
        "pitch_condition"
    ]
    
    # Bookmaker sources
    BOOKMAKERS = ["Hollywoodbets", "Betway"]

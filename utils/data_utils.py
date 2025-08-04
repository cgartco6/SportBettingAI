def calculate_accuracy(y_true, y_pred):
    """Calculate prediction accuracy"""
    return np.mean(y_true == y_pred)

def preprocess_prediction_data(raw_data):
    """Prepare raw data for prediction"""
    # Feature engineering specifically for prediction
    if raw_data is None or raw_data.empty:
        return pd.DataFrame()
    
    # Create feature: form differential
    raw_data["form_differential"] = raw_data["home_form"] - raw_data["away_form"]
    
    # Create feature: injury impact differential
    raw_data["injury_differential"] = (
        raw_data["home_injury_impact"] - raw_data["away_injury_impact"]
    )
    
    # Create feature: coach rating differential
    raw_data["coach_differential"] = (
        raw_data["home_coach_rating"] - raw_data["away_coach_rating"]
    )
    
    # Select required features
    return raw_data[Config.REQUIRED_FEATURES + ["match_id", "home_team", "away_team"]]

def calculate_injury_impact(home_injuries, away_injuries):
    """Calculate injury impact score (0-1)"""
    # Implementation would analyze player importance
    return min(len(home_injuries) * 0.1, 1.0), min(len(away_injuries) * 0.1, 1.0)

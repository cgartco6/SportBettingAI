import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from config import Config

def preprocess_data(raw_data, target_column=Config.TARGET):
    """
    Preprocess raw data for model training
    """
    # Handle missing values
    data = raw_data.copy()
    data.fillna({
        'player_form': data['player_form'].median(),
        'team_form': 0.5,  # Neutral form
        'coach_form': 0.5,
        'injuries': 0,  # No injuries
        'home_away': 0,  # Neutral ground
        'transfers': 0,  # No transfers
        'weather': 1.0,  # Perfect conditions
        'pitch_condition': 1.0  # Perfect pitch
    }, inplace=True)
    
    # Feature engineering
    data = create_features(data)
    
    # Split features and target
    X = data[Config.REQUIRED_FEATURES]
    y = data[target_column]
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = MinMaxScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
    
    return X_train, X_test, y_train, y_test, scaler

def create_features(data):
    """Create additional features for modeling"""
    # Form differential
    data['form_differential'] = data['home_form'] - data['away_form']
    
    # Injury impact
    data['injury_impact'] = data['home_injuries'] * 0.8 + data['away_injuries'] * 0.2
    
    # Coach experience differential
    data['coach_exp_diff'] = data['home_coach_exp'] - data['away_coach_exp']
    
    # Weather impact (0 = bad, 1 = good)
    weather_impact = {
        'sunny': 1.0,
        'cloudy': 0.9,
        'rainy': 0.7,
        'snowy': 0.5
    }
    data['weather_impact'] = data['weather'].map(weather_impact).fillna(0.8)
    
    # Pitch condition impact
    data['pitch_impact'] = data['pitch_condition'] / 10.0
    
    # Add new features to required features
    Config.REQUIRED_FEATURES.extend([
        'form_differential',
        'injury_impact',
        'coach_exp_diff',
        'weather_impact',
        'pitch_impact'
    ])
    
    return data

def calculate_accuracy(y_true, y_pred):
    """Calculate prediction accuracy"""
    return np.mean(y_true == y_pred)

def calculate_form_index(home_players, away_players):
    """Calculate form index from player data"""
    # Implementation would analyze player performance metrics
    home_form = np.mean([p['form'] for p in home_players]) if home_players else 0.5
    away_form = np.mean([p['form'] for p in away_players]) if away_players else 0.5
    return home_form, away_form

def calculate_injury_impact(home_injuries, away_injuries):
    """Calculate injury impact score (0-1)"""
    # Implementation would analyze player importance
    home_impact = min(len(home_injuries) * 0.1, 1.0)
    away_impact = min(len(away_injuries) * 0.1, 1.0)
    return home_impact, away_impact

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from config import Config

def preprocess_data(raw_data, target_column=Config.TARGET):
    data = raw_data.copy()
    data.fillna({
        'player_form': data['player_form'].median(),
        'team_form': 0.5,
        'coach_form': 0.5,
        'injuries': 0,
        'home_away': 0,
        'transfers': 0,
        'weather': 1.0,
        'pitch_condition': 1.0
    }, inplace=True)
    
    data = create_features(data)
    
    X = data[Config.REQUIRED_FEATURES]
    y = data[target_column]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    scaler = MinMaxScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
    
    return X_train, X_test, y_train, y_test, scaler

def create_features(data):
    data['form_differential'] = data['home_form'] - data['away_form']
    data['injury_impact'] = data['home_injuries'] * 0.8 + data['away_injuries'] * 0.2
    data['coach_exp_diff'] = data['home_coach_exp'] - data['away_coach_exp']
    
    weather_impact = {
        'sunny': 1.0,
        'cloudy': 0.9,
        'rainy': 0.7,
        'snowy': 0.5
    }
    data['weather_impact'] = data['weather'].map(weather_impact).fillna(0.8)
    data['pitch_impact'] = data['pitch_condition'] / 10.0
    
    Config.REQUIRED_FEATURES.extend([
        'form_differential',
        'injury_impact',
        'coach_exp_diff',
        'weather_impact',
        'pitch_impact'
    ])
    
    return data

def calculate_accuracy(y_true, y_pred):
    return np.mean(y_true == y_pred)

def calculate_form_index(home_players, away_players):
    home_form = np.mean([p['form'] for p in home_players]) if home_players else 0.5
    away_form = np.mean([p['form'] for p in away_players]) if away_players else 0.5
    return home_form, away_form

def calculate_injury_impact(home_injuries, away_injuries):
    home_impact = min(len(home_injuries) * 0.1, 1.0)
    away_impact = min(len(away_injuries) * 0.1, 1.0)
    return home_impact, away_impact

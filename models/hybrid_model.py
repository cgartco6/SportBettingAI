import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import plotly.graph_objects as go
from config import Config
import os

class HybridModel:
    def __init__(self, model_name="dc_btts_predictor"):
        self.model_name = model_name
        self.gbm = None
        self.lstm = None
        self.feature_importances = None
        self.input_shape = None
        
    def train(self, data, target="dc_btts", validation_split=0.2):
        X = data.drop(columns=[target])
        y = data[target]
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        self.train_gbm(X_train, y_train)
        
        important_features = self.get_important_features(threshold=0.01)
        X_train_important = X_train[important_features]
        X_val_important = X_val[important_features]
        
        self.train_lstm(X_train_important, y_train, X_val_important, y_val)
        
        val_accuracy = self.evaluate(X_val, y_val)
        print(f"Hybrid model validation accuracy: {val_accuracy:.2%}")
        
        return val_accuracy
    
    def train_gbm(self, X_train, y_train):
        self.gbm = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=5,
            random_state=42,
            subsample=0.8
        )
        self.gbm.fit(X_train, y_train)
        
        self.feature_importances = pd.Series(
            self.gbm.feature_importances_,
            index=X_train.columns
        ).sort_values(ascending=False)
    
    def get_important_features(self, threshold=0.01):
        return self.feature_importances[
            self.feature_importances > threshold
        ].index.tolist()
    
    def train_lstm(self, X_train, y_train, X_val, y_val):
        X_train_seq = X_train.values.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_val_seq = X_val.values.reshape((X_val.shape[0], X_val.shape[1], 1))
        
        self.lstm = Sequential([
            LSTM(128, input_shape=(X_train_seq.shape[1], 1), return_sequences=True),
            Dropout(0.3),
            LSTM(64),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        self.lstm.compile(
            loss='binary_crossentropy',
            optimizer='adam',
            metrics=['accuracy']
        )
        
        self.lstm.fit(
            X_train_seq, y_train,
            validation_data=(X_val_seq, y_val),
            epochs=50,
            batch_size=32,
            verbose=1
        )
    
    def predict_proba(self, X):
        important_features = self.get_important_features(threshold=0.01)
        X_important = X[important_features]
        
        X_seq = X_important.values.reshape((X_important.shape[0], X_important.shape[1], 1))
        
        gbm_proba = self.gbm.predict_proba(X)[:, 1]
        lstm_proba = self.lstm.predict(X_seq).flatten()
        
        hybrid_proba = (0.6 * gbm_proba) + (0.4 * lstm_proba)
        
        return hybrid_proba
    
    def predict(self, X, threshold=0.5):
        proba = self.predict_proba(X)
        return (proba >= threshold).astype(int)
    
    def evaluate(self, X, y):
        predictions = self.predict(X)
        return accuracy_score(y, predictions)
    
    def save(self, version="v1"):
        model_dir = f"{Config.MODEL_PATH}{self.model_name}/{version}/"
        os.makedirs(model_dir, exist_ok=True)
        
        joblib.dump(self.gbm, f"{model_dir}gbm_model.pkl")
        self.lstm.save(f"{model_dir}lstm_model.keras")
        self.feature_importances.to_csv(f"{model_dir}feature_importances.csv")
        
        print(f"Model saved to {model_dir}")
    
    def load(self, version="v1"):
        model_dir = f"{Config.MODEL_PATH}{self.model_name}/{version}/"
        
        self.gbm = joblib.load(f"{model_dir}gbm_model.pkl")
        self.lstm = load_model(f"{model_dir}lstm_model.keras")
        self.feature_importances = pd.read_csv(
            f"{model_dir}feature_importances.csv", 
            index_col=0,
            squeeze=True
        )
        
        print(f"Model loaded from {model_dir}")
        return self
    
    def feature_importance_plot(self):
        if self.feature_importances is None:
            return None
        
        top_features = self.feature_importances.head(15)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top_features.values,
            y=top_features.index,
            orientation='h',
            marker_color='#2ECCFA'
        ))
        
        fig.update_layout(
            title='Top Predictive Features',
            xaxis_title='Importance Score',
            yaxis_title='Feature',
            template='plotly_dark',
            height=600
        )
        
        return fig

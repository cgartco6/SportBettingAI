import os
from config import Config
import joblib
import pandas as pd

class ModelRegistry:
    def __init__(self):
        self.models = {}
        self.model_versions = {}
        self.performance_history = {}
        
    def register_model(self, model_name, model, version="v1"):
        self.models[model_name] = model
        self.model_versions[model_name] = version
        print(f"Registered model: {model_name} (version {version})")
        
    def get_model(self, model_name):
        model = self.models.get(model_name)
        if model is None:
            print(f"Model {model_name} not found in registry")
        return model
    
    def load_model(self, model_name, version="latest"):
        if version == "latest":
            model_dir = f"{Config.MODEL_PATH}{model_name}/"
            if not os.path.exists(model_dir):
                print(f"Model directory not found: {model_dir}")
                return None
            
            versions = [d for d in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, d))]
            if not versions:
                print(f"No versions found for model {model_name}")
                return None
                
            version = sorted(versions)[-1]
        
        model_path = f"{Config.MODEL_PATH}{model_name}/{version}/"
        
        if not os.path.exists(model_path):
            print(f"Model path not found: {model_path}")
            return None
            
        from .hybrid_model import HybridModel
        model = HybridModel(model_name)
        model.load(version)
        
        self.register_model(model_name, model, version)
        return model
    
    def save_model(self, model_name, model, version="v1"):
        model.save(version)
        self.register_model(model_name, model, version)
    
    def track_performance(self, model_name, metrics):
        if model_name not in self.performance_history:
            self.performance_history[model_name] = []
            
        self.performance_history[model_name].append({
            "timestamp": pd.Timestamp.now(),
            **metrics
        })
        
    def get_performance_history(self, model_name):
        return self.performance_history.get(model_name, [])
    
    def compare_models(self, model_name):
        history = self.get_performance_history(model_name)
        if not history:
            return pd.DataFrame()
            
        df = pd.DataFrame(history)
        df.set_index("timestamp", inplace=True)
        df["version"] = df.index.map(lambda x: self.model_versions.get(model_name, "unknown"))
        return df
    
    def get_best_model(self, model_name, metric="accuracy"):
        history = self.get_performance_history(model_name)
        if not history:
            return None
            
        best_performance = max(history, key=lambda x: x.get(metric, 0))
        best_version = self.model_versions.get(model_name, "unknown")
        return self.load_model(model_name, best_version)

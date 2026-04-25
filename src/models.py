# src/models.py
import numpy as np
import pickle
import os
from typing import Dict, Tuple
from sklearn.preprocessing import StandardScaler
from river import linear_model, preprocessing, compose
import lightgbm as lgb
from config import Config
from logging_utils import logger

class ModelManager:
    """Manage prediction models"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        
        # Online learning model (River)
        self.river_model = compose.Pipeline(
            preprocessing.StandardScaler(),
            linear_model.LogisticRegression(
                optimizer=None,  # Use SGD
                loss='log_loss'
            )
        )
        
        # LightGBM model (batch learning)
        self.lgb_model = None
        self.feature_names = None
        
        # Load existing models if available
        self.load_models()
    
    def load_models(self):
        """Load saved models from disk"""
        try:
            river_path = os.path.join(Config.MODELS_DIR, "river_model.pkl")
            lgb_path = os.path.join(Config.MODELS_DIR, "lgb_model.txt")
            
            if os.path.exists(river_path):
                with open(river_path, 'rb') as f:
                    self.river_model = pickle.load(f)
                logger.info("✅ Loaded River model")
            
            if os.path.exists(lgb_path):
                self.lgb_model = lgb.Booster(model_file=lgb_path)
                logger.info("✅ Loaded LightGBM model")
        
        except Exception as e:
            logger.warning(f"⚠️ Could not load models: {e}")
    
    def save_models(self):
        """Save models to disk"""
        try:
            river_path = os.path.join(Config.MODELS_DIR, "river_model.pkl")
            with open(river_path, 'wb') as f:
                pickle.dump(self.river_model, f)
            logger.info("✅ Saved River model")
            
            if self.lgb_model:
                lgb_path = os.path.join(Config.MODELS_DIR, "lgb_model.txt")
                self.lgb_model.save_model(lgb_path)
                logger.info("✅ Saved LightGBM model")
        
        except Exception as e:
            logger.error(f"❌ Error saving models: {e}")
    
    def predict_river(self, features: Dict[str, float]) -> float:
        """Get prediction from River model"""
        try:
            proba = self.river_model.predict_proba_one(features)
            if proba:
                confidence = max(proba.values())
            else:
                confidence = 0.5
            return confidence
        except Exception as e:
            logger.warning(f"⚠️ River prediction error: {e}")
            return 0.5
    
    def predict_lgb(self, features: Dict[str, float]) -> float:
        """Get prediction from LightGBM model"""
        try:
            if not self.lgb_model or not self.feature_names:
                return 0.5
            
            # Ensure all features present
            X = np.array([[features.get(f, 0) for f in self.feature_names]])
            prediction = self.lgb_model.predict(X)
            return float(prediction[0]) if len(prediction) > 0 else 0.5
        
        except Exception as e:
            logger.warning(f"⚠️ LightGBM prediction error: {e}")
            return 0.5
    
    def predict_ensemble(self, features: Dict[str, float]) -> Tuple[float, str]:
        """Ensemble prediction (average of models)"""
        try:
            river_pred = self.predict_river(features)
            lgb_pred = self.predict_lgb(features)
            
            # Weight: if LGB exists, use both; else River only
            if self.lgb_model:
                ensemble_pred = (river_pred * 0.4 + lgb_pred * 0.6)
                model_used = "Ensemble (River+LGB)"
            else:
                ensemble_pred = river_pred
                model_used = "River"
            
            return float(ensemble_pred), model_used
        
        except Exception as e:
            logger.warning(f"⚠️ Ensemble prediction error: {e}")
            return 0.5, "Error"
    
    def learn_from_trade(self, features: Dict[str, float], outcome: int):
        """Online learning from trade outcome"""
        try:
            # Learn with River
            self.river_model = self.river_model.learn_one(features, outcome)
            
            logger.debug(f"✅ Model learned from outcome: {outcome}")
        
        except Exception as e:
            logger.warning(f"⚠️ Learning error: {e}")
    
    def train_lgb(self, X_train: np.ndarray, y_train: np.ndarray, feature_names: list):
        """Train LightGBM model (batch)"""
        try:
            self.feature_names = feature_names
            
            dataset = lgb.Dataset(X_train, label=y_train, feature_names=feature_names)
            
            params = {
                'objective': 'binary',
                'metric': 'auc',
                'learning_rate': 0.05,
                'max_depth': 5,
                'num_leaves': 31,
                'verbose': -1
            }
            
            self.lgb_model = lgb.train(
                params,
                dataset,
                num_boost_round=100
            )
            
            self.save_models()
            logger.info("✅ LightGBM model trained and saved")
        
        except Exception as e:
            logger.error(f"❌ LightGBM training error: {e}")

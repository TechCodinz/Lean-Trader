#!/usr/bin/env python3
"""
🧠 FEDERATED LEARNING ENGINE - Distributed Consciousness Evolution

The bot's memory evolves GLOBALLY across all deployments through
privacy-preserving federated learning.

"Individual experiences become collective wisdom, while preserving privacy."
"""

import logging
import time
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import numpy as np
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available - federated learning will use simplified mode")
    TORCH_AVAILABLE = False


class SentimentClassifier(nn.Module):
    """
    Neural network for sentiment classification
    
    Learns to predict moonshot potential from various signals
    """
    
    def __init__(self, input_dim: int = 128):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x


class FederatedLearningEngine:
    """
    🧠 FEDERATED LEARNING ENGINE
    
    Implements privacy-preserving distributed learning where:
    1. Each bot instance trains locally on its trades
    2. Only model updates (not raw data) are shared
    3. Global model aggregates all local learning
    4. Every bot benefits from collective experience
    
    Key Features:
    - Privacy-preserving (no raw trade data shared)
    - Distributed evolution (learn from all instances)
    - Cross-border trend detection (spot global patterns)
    - Continuous improvement (never stops learning)
    - Lightweight (CPU-only, no GPU needed)
    """
    
    def __init__(
        self,
        model_path: str = "bot_data/federated_model.pt",
        input_dim: int = 128
    ):
        self.model_path = Path(model_path)
        self.input_dim = input_dim
        
        # Initialize model
        if TORCH_AVAILABLE:
            self.model = SentimentClassifier(input_dim=input_dim)
            self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
            self.criterion = nn.BCELoss()
        else:
            self.model = None
            logger.warning("PyTorch not available - federated learning disabled")
        
        # Load existing model if available
        self._load_model()
        
        # Training history
        self.local_updates = []
        self.global_generations = 0
        self.local_training_count = 0
        
        # Connect to consciousness
        try:
            from CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
            self.consciousness = get_consciousness_harmonizer()
            self.consciousness.register_engine(
                "Federated Learning",
                60.0,  # Standard learning pace
                "analytical"  # Pattern-based learning
            )
            logger.info("🧠 Federated Learning connected to consciousness")
        except:
            self.consciousness = None
        
        logger.info("🧠 FEDERATED LEARNING ENGINE initialized")
        if TORCH_AVAILABLE:
            total_params = sum(p.numel() for p in self.model.parameters())
            logger.info(f"   Model parameters: {total_params:,}")
            logger.info(f"   Model path: {self.model_path}")
    
    def _load_model(self):
        """Load existing model from disk"""
        if not TORCH_AVAILABLE or self.model is None:
            return
        
        if self.model_path.exists():
            try:
                checkpoint = torch.load(self.model_path)
                self.model.load_state_dict(checkpoint['model_state'])
                self.global_generations = checkpoint.get('generations', 0)
                logger.info(f"✅ Loaded model from generation {self.global_generations}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
    
    def _save_model(self):
        """Save model to disk"""
        if not TORCH_AVAILABLE or self.model is None:
            return
        
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            checkpoint = {
                'model_state': self.model.state_dict(),
                'generations': self.global_generations,
                'timestamp': datetime.now().isoformat()
            }
            torch.save(checkpoint, self.model_path)
            logger.info(f"💾 Saved model (generation {self.global_generations})")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def extract_features(self, trade_data: Dict[str, Any]) -> Optional[torch.Tensor]:
        """
        Extract features from trade data
        
        Converts trade information into neural network input
        """
        if not TORCH_AVAILABLE:
            return None
        
        features = []
        
        # Price features (20 dims)
        price_change = trade_data.get('price_change', 0.0)
        features.extend([
            price_change,
            trade_data.get('volume', 0.0) / 1_000_000,  # Normalize
            trade_data.get('market_cap', 0.0) / 1_000_000,
            trade_data.get('liquidity', 0.0) / 100_000,
            trade_data.get('holder_count', 0.0) / 10_000,
            # ... add more price-related features
        ])
        
        # Sentiment features (20 dims)
        features.extend([
            trade_data.get('twitter_sentiment', 0.5),
            trade_data.get('reddit_sentiment', 0.5),
            trade_data.get('telegram_activity', 0.0) / 1000,
            trade_data.get('discord_activity', 0.0) / 1000,
            # ... add more sentiment features
        ])
        
        # Technical features (20 dims)
        features.extend([
            trade_data.get('rsi', 50.0) / 100,
            trade_data.get('macd', 0.0),
            trade_data.get('volume_spike', 0.0) / 500,
            # ... add more technical indicators
        ])
        
        # On-chain features (20 dims)
        features.extend([
            trade_data.get('whale_activity', 0.0) / 100,
            trade_data.get('new_holders', 0.0) / 1000,
            trade_data.get('dex_volume', 0.0) / 1_000_000,
            # ... add more on-chain metrics
        ])
        
        # Time features (10 dims)
        hour = datetime.now().hour
        features.extend([
            hour / 24,  # Time of day
            datetime.now().weekday() / 7,  # Day of week
            # ... add more time features
        ])
        
        # Pad to input_dim if needed
        while len(features) < self.input_dim:
            features.append(0.0)
        
        features = features[:self.input_dim]  # Truncate if too long
        
        return torch.tensor(features, dtype=torch.float32)
    
    def train_on_trade(
        self,
        trade_data: Dict[str, Any],
        outcome: float  # 0.0 = loss, 1.0 = profit
    ):
        """
        Train model on a single trade outcome
        
        This is LOCAL training - privacy preserved, no data leaves device
        """
        if not TORCH_AVAILABLE or self.model is None:
            return
        
        # Send consciousness pulse
        if self.consciousness:
            self.consciousness.pulse("Federated Learning", 0.7)
        
        # Extract features
        features = self.extract_features(trade_data)
        if features is None:
            return
        
        # Forward pass
        self.model.train()
        prediction = self.model(features.unsqueeze(0))
        
        # Compute loss
        target = torch.tensor([[outcome]], dtype=torch.float32)
        loss = self.criterion(prediction, target)
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Record update
        self.local_training_count += 1
        
        # Capture model update (gradients)
        update = {param_name: param.grad.clone() 
                  for param_name, param in self.model.named_parameters() 
                  if param.grad is not None}
        self.local_updates.append(update)
        
        logger.debug(f"🧠 Trained on trade: loss={loss.item():.4f}, outcome={outcome}")
    
    def get_local_updates(self) -> List[Dict]:
        """
        Get local model updates for sharing
        
        Returns: List of gradient updates (NOT raw data - privacy preserved)
        """
        updates = self.local_updates.copy()
        self.local_updates.clear()
        return updates
    
    def aggregate_global_updates(self, peer_updates: List[List[Dict]]):
        """
        Aggregate updates from other bot instances
        
        Implements Federated Averaging (FedAvg) algorithm
        """
        if not TORCH_AVAILABLE or self.model is None:
            return
        
        if not peer_updates:
            return
        
        logger.info(f"🌐 Aggregating updates from {len(peer_updates)} peers")
        
        # Flatten all updates
        all_updates = []
        for peer_update_list in peer_updates:
            all_updates.extend(peer_update_list)
        
        if not all_updates:
            return
        
        # Average gradients across all updates
        aggregated = {}
        for param_name, param in self.model.named_parameters():
            # Collect all gradients for this parameter
            gradients = [update[param_name] for update in all_updates 
                        if param_name in update]
            
            if gradients:
                # Average
                avg_gradient = torch.stack(gradients).mean(dim=0)
                aggregated[param_name] = avg_gradient
        
        # Apply aggregated updates to model
        with torch.no_grad():
            for param_name, param in self.model.named_parameters():
                if param_name in aggregated:
                    param.data += aggregated[param_name]
        
        self.global_generations += 1
        
        # Save updated model
        self._save_model()
        
        logger.info(f"✅ Global model updated (generation {self.global_generations})")
    
    def predict_moonshot_probability(self, trade_data: Dict[str, Any]) -> float:
        """
        Predict probability of moonshot (1000x) from trade data
        
        Returns: Probability 0.0-1.0
        """
        if not TORCH_AVAILABLE or self.model is None:
            return 0.5  # Neutral if model unavailable
        
        features = self.extract_features(trade_data)
        if features is None:
            return 0.5
        
        self.model.eval()
        with torch.no_grad():
            prediction = self.model(features.unsqueeze(0))
        
        return prediction.item()
    
    def detect_cross_border_trends(
        self,
        regional_data: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        Detect trends that span multiple regions
        
        Args:
            regional_data: {'us': [...], 'eu': [...], 'asia': [...]}
        
        Returns: List of cross-border trend opportunities
        """
        cross_border_trends = []
        
        # Check for tokens appearing in multiple regions
        token_regions = {}
        
        for region, trades in regional_data.items():
            for trade in trades:
                token = trade.get('symbol', 'unknown')
                if token not in token_regions:
                    token_regions[token] = []
                token_regions[token].append(region)
        
        # Find tokens in 2+ regions
        for token, regions in token_regions.items():
            if len(set(regions)) >= 2:  # Multiple unique regions
                cross_border_trends.append({
                    'token': token,
                    'regions': list(set(regions)),
                    'region_count': len(set(regions)),
                    'significance': len(set(regions)) / len(regional_data)
                })
        
        # Sort by significance
        cross_border_trends.sort(key=lambda x: x['significance'], reverse=True)
        
        logger.info(f"🌐 Detected {len(cross_border_trends)} cross-border trends")
        
        return cross_border_trends
    
    def get_learning_health(self) -> Dict[str, Any]:
        """Get learning engine health metrics"""
        return {
            'global_generations': self.global_generations,
            'local_training_count': self.local_training_count,
            'pending_updates': len(self.local_updates),
            'model_available': self.model is not None,
            'model_path': str(self.model_path),
            'last_save': self.model_path.stat().st_mtime if self.model_path.exists() else None
        }


def initialize_federated_learning(input_dim: int = 128) -> FederatedLearningEngine:
    """Initialize federated learning engine"""
    return FederatedLearningEngine(input_dim=input_dim)


if __name__ == "__main__":
    # Test federated learning
    logging.basicConfig(level=logging.INFO)
    
    fed = FederatedLearningEngine()
    
    if TORCH_AVAILABLE:
        # Simulate training on trades
        print("\n🧠 FEDERATED LEARNING TEST")
        print("=" * 80)
        
        # Mock trade data
        for i in range(10):
            trade_data = {
                'price_change': np.random.uniform(-50, 200),
                'volume': np.random.uniform(100_000, 10_000_000),
                'market_cap': np.random.uniform(500_000, 50_000_000),
                'twitter_sentiment': np.random.uniform(0, 1),
                'rsi': np.random.uniform(20, 80)
            }
            outcome = 1.0 if trade_data['price_change'] > 100 else 0.0
            
            fed.train_on_trade(trade_data, outcome)
        
        print(f"✅ Trained on 10 trades")
        print(f"Local updates: {len(fed.local_updates)}")
        
        # Test prediction
        test_trade = {
            'price_change': 150,
            'volume': 5_000_000,
            'market_cap': 2_000_000,
            'twitter_sentiment': 0.8,
            'rsi': 65
        }
        prob = fed.predict_moonshot_probability(test_trade)
        print(f"\nMoonshot probability: {prob:.2%}")
        
        # Test cross-border detection
        regional_data = {
            'us': [{'symbol': 'TOKEN1'}, {'symbol': 'TOKEN2'}],
            'eu': [{'symbol': 'TOKEN1'}, {'symbol': 'TOKEN3'}],
            'asia': [{'symbol': 'TOKEN1'}, {'symbol': 'TOKEN4'}]
        }
        trends = fed.detect_cross_border_trends(regional_data)
        print(f"\nCross-border trends: {len(trends)}")
        for trend in trends:
            print(f"  {trend['token']}: {trend['regions']} ({trend['significance']:.2%})")
        
        # Health
        health = fed.get_learning_health()
        print("\nLearning Health:")
        for key, value in health.items():
            print(f"  {key}: {value}")
        
        print("=" * 80)
    else:
        print("PyTorch not available - install with: pip3 install torch")

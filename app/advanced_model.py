"""
Advanced Model Manager for Sentiment Analysis
Supports multiple models, comparison, and batch processing
"""

import logging
import time
import json
import sys
import os
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from transformers import pipeline
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

logger = logging.getLogger('sentiment_analyzer.advanced_model')

@dataclass
class ModelResult:
    """Result from a single model prediction"""
    model_name: str
    sentiment: str
    confidence: float
    processing_time: float
    timestamp: datetime

@dataclass
class ComparisonResult:
    """Result from comparing multiple models"""
    text: str
    results: List[ModelResult]
    consensus_sentiment: str
    average_confidence: float
    agreement_score: float  # How much models agree (0-1)
    processing_time: float

class AdvancedSentimentAnalyzer:
    """Advanced sentiment analyzer with multiple models and comparison capabilities"""
    
    def __init__(self):
        self.models = {}
        self.model_configs = {
            'primary': {
                'name': 'fitsblb/YelpReviewsAnalyzer',
                'label_mapping': {'LABEL_0': 'Negative', 'LABEL_1': 'Positive'}
            },
            'distilbert': {
                'name': 'distilbert-base-uncased-finetuned-sst-2-english',
                'label_mapping': {'NEGATIVE': 'Negative', 'POSITIVE': 'Positive'}
            },
            'cardiffnlp': {
                'name': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
                'label_mapping': {'LABEL_0': 'Negative', 'LABEL_1': 'Neutral', 'LABEL_2': 'Positive'}
            },
            'finbert': {
                'name': 'ProsusAI/finbert',
                'label_mapping': {'negative': 'Negative', 'neutral': 'Neutral', 'positive': 'Positive'}
            }
        }
        self.performance_stats = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all available models"""
        logger.info("Initializing advanced model manager...")
        
        for model_key, model_config in self.model_configs.items():
            try:
                logger.info(f"Loading model: {model_config['name']}")
                start_time = time.time()
                
                # Try to load the model
                model = pipeline(
                    "sentiment-analysis",
                    model=model_config['name'],
                    return_all_scores=True,
                    device=0 if torch.cuda.is_available() else -1
                )
                
                # Test the model
                test_result = model("This is a test.")
                logger.info(f"Model {model_key} test successful: {test_result}")
                
                load_time = time.time() - start_time
                self.models[model_key] = model
                self.performance_stats[model_key] = {
                    'load_time': load_time,
                    'predictions': 0,
                    'total_time': 0,
                    'errors': 0
                }
                
                logger.info(f"✅ Model {model_key} loaded successfully in {load_time:.2f}s")
                
            except Exception as e:
                logger.warning(f"❌ Failed to load model {model_key}: {e}")
                # Don't fail completely, just skip this model
                continue
        
        if not self.models:
            raise Exception("No models could be loaded!")
        
        logger.info(f"✅ Advanced model manager initialized with {len(self.models)} models")
    
    def predict_single_model(self, text: str, model_key: str) -> ModelResult:
        """Predict sentiment using a single model"""
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not available")
        
        start_time = time.time()
        
        try:
            model = self.models[model_key]
            model_config = self.model_configs[model_key]
            
            # Get prediction
            raw_result = model(text)
            
            # Handle different output formats
            if isinstance(raw_result, list) and len(raw_result) > 0:
                if isinstance(raw_result[0], list):
                    # Handle nested list format [[{...}]]
                    scores = raw_result[0]
                else:
                    # Handle direct list format [{...}]
                    scores = raw_result
            else:
                scores = raw_result
            
            # Find the highest confidence prediction
            best_prediction = max(scores, key=lambda x: x['score'])
            
            # Map label to human-readable format
            raw_label = best_prediction['label']
            mapped_label = model_config['label_mapping'].get(raw_label, raw_label)
            
            processing_time = time.time() - start_time
            
            # Update stats
            self.performance_stats[model_key]['predictions'] += 1
            self.performance_stats[model_key]['total_time'] += processing_time
            
            return ModelResult(
                model_name=model_config['name'],
                sentiment=mapped_label,
                confidence=best_prediction['score'],
                processing_time=processing_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.performance_stats[model_key]['errors'] += 1
            processing_time = time.time() - start_time
            logger.error(f"Error in model {model_key}: {e}")
            
            return ModelResult(
                model_name=model_config['name'],
                sentiment="Error",
                confidence=0.0,
                processing_time=processing_time,
                timestamp=datetime.now()
            )
    
    def predict_with_comparison(self, text: str, models: Optional[List[str]] = None) -> ComparisonResult:
        """Predict sentiment using multiple models and compare results"""
        if models is None:
            models = list(self.models.keys())
        
        start_time = time.time()
        results = []
        
        # Use ThreadPoolExecutor for parallel predictions
        with ThreadPoolExecutor(max_workers=len(models)) as executor:
            future_to_model = {
                executor.submit(self.predict_single_model, text, model): model 
                for model in models if model in self.models
            }
            
            for future in as_completed(future_to_model):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    model_name = future_to_model[future]
                    logger.error(f"Model {model_name} failed: {e}")
        
        # Calculate consensus and agreement
        valid_results = [r for r in results if r.sentiment != "Error"]
        
        if not valid_results:
            # All models failed
            consensus_sentiment = "Error"
            average_confidence = 0.0
            agreement_score = 0.0
        else:
            # Find consensus sentiment (most common)
            sentiment_votes = {}
            confidence_sum = 0
            
            for result in valid_results:
                sentiment = result.sentiment
                sentiment_votes[sentiment] = sentiment_votes.get(sentiment, 0) + result.confidence
                confidence_sum += result.confidence
            
            consensus_sentiment = max(sentiment_votes, key=sentiment_votes.get)
            average_confidence = confidence_sum / len(valid_results)
            
            # Calculate agreement score (how many models agree with consensus)
            agreeing_models = sum(1 for r in valid_results if r.sentiment == consensus_sentiment)
            agreement_score = agreeing_models / len(valid_results)
        
        total_time = time.time() - start_time
        
        return ComparisonResult(
            text=text,
            results=results,
            consensus_sentiment=consensus_sentiment,
            average_confidence=average_confidence,
            agreement_score=agreement_score,
            processing_time=total_time
        )
    
    def batch_predict(self, texts: List[str], model_key: Optional[str] = None) -> List[ModelResult]:
        """Predict sentiment for multiple texts"""
        if model_key and model_key not in self.models:
            raise ValueError(f"Model {model_key} not available")
        
        # Use first available model if none specified
        if model_key is None:
            model_key = list(self.models.keys())[0]
        
        logger.info(f"Processing batch of {len(texts)} texts with model {model_key}")
        
        results = []
        for i, text in enumerate(texts):
            try:
                result = self.predict_single_model(text, model_key)
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(texts)} texts")
                    
            except Exception as e:
                logger.error(f"Error processing text {i}: {e}")
                results.append(ModelResult(
                    model_name=self.model_configs[model_key]['name'],
                    sentiment="Error",
                    confidence=0.0,
                    processing_time=0.0,
                    timestamp=datetime.now()
                ))
        
        return results
    
    def get_model_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all models"""
        performance = {}
        
        for model_key, stats in self.performance_stats.items():
            if stats['predictions'] > 0:
                avg_time = stats['total_time'] / stats['predictions']
                error_rate = stats['errors'] / (stats['predictions'] + stats['errors'])
            else:
                avg_time = 0
                error_rate = 0
            
            performance[model_key] = {
                'model_name': self.model_configs[model_key]['name'],
                'total_predictions': stats['predictions'],
                'total_errors': stats['errors'],
                'average_processing_time': avg_time,
                'error_rate': error_rate,
                'load_time': stats['load_time']
            }
        
        return performance
    
    def get_available_models(self) -> List[str]:
        """Get list of successfully loaded models"""
        return list(self.models.keys())

# Global instance
advanced_analyzer = None

def get_advanced_analyzer() -> AdvancedSentimentAnalyzer:
    """Get or create the global advanced analyzer instance"""
    global advanced_analyzer
    if advanced_analyzer is None:
        advanced_analyzer = AdvancedSentimentAnalyzer()
    return advanced_analyzer

# Convenience functions for backward compatibility
def predict_advanced(text: str, models: Optional[List[str]] = None) -> ComparisonResult:
    """Predict with model comparison"""
    analyzer = get_advanced_analyzer()
    return analyzer.predict_with_comparison(text, models)

def predict_batch(texts: List[str], model_key: Optional[str] = None) -> List[ModelResult]:
    """Predict sentiment for multiple texts"""
    analyzer = get_advanced_analyzer()
    return analyzer.batch_predict(texts, model_key)

def get_model_stats() -> Dict[str, Dict[str, Any]]:
    """Get model performance statistics"""
    analyzer = get_advanced_analyzer()
    return analyzer.get_model_performance()

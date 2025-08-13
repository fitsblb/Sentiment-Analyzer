import os
import sys
from transformers import pipeline
from typing import Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from config.logging_config import get_logger

# Initialize logger
logger = get_logger('model')


class ModelError(Exception):
    """Custom exception for model-related errors."""
    pass


class SentimentAnalyzer:
    """Sentiment analysis model wrapper with error handling and caching."""
    
    def __init__(self):
        self.pipeline = None
        self.model_name = config.MODEL_NAME
        self._load_model()
    
    def _load_model(self):
        """Load the sentiment analysis model with error handling and fallback."""
        try:
            logger.info(f"Loading sentiment analysis model: {self.model_name}")
            
            # Try loading the primary model first
            try:
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.model_name,
                    top_k=1
                )
                logger.info("Primary model loaded successfully")
                
            except Exception as primary_error:
                logger.warning(f"Primary model failed to load: {primary_error}")
                logger.info("Trying fallback model: distilbert-base-uncased-finetuned-sst-2-english")
                
                # Fallback to a reliable model
                fallback_model = "distilbert-base-uncased-finetuned-sst-2-english"
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model=fallback_model,
                    top_k=1
                )
                self.model_name = fallback_model  # Update model name for logging
                logger.info("Fallback model loaded successfully")
            
            # Test the model with a simple prediction
            test_result = self.pipeline("This is a test.")
            logger.debug(f"Model test successful: {test_result}")
            
        except Exception as e:
            logger.error(f"Failed to load any sentiment analysis model: {e}")
            raise ModelError(f"Could not load sentiment analysis model: {e}")
    
    def predict(self, text: str) -> Tuple[str, float]:
        """
        Predict sentiment for given text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (sentiment_label, confidence_score)
            
        Raises:
            ModelError: If prediction fails
        """
        try:
            if not self.pipeline:
                raise ModelError("Model not loaded")
            
            logger.debug(f"Running sentiment prediction on text of length {len(text)}")
            
            # Run prediction
            output = self.pipeline(text)
            
            if not output or len(output) == 0:
                raise ModelError("Model returned empty prediction")
            
            # Handle different output formats from different models
            if isinstance(output[0], list):
                # Some models return nested lists
                result = output[0][0] if output[0] else output[0]
            else:
                # Standard format
                result = output[0]
            
            raw_label = result["label"]
            score = result["score"]
            
            # Map model labels to human-readable labels
            sentiment = self._map_sentiment_label(raw_label)
            
            logger.debug(f"Prediction completed: {sentiment} (confidence: {score:.3f})")
            
            return sentiment, float(score)
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise ModelError(f"Sentiment prediction failed: {e}")
    
    def _map_sentiment_label(self, label: str) -> str:
        """
        Map model output labels to human-readable sentiment labels.
        
        Args:
            label: Raw label from model
            
        Returns:
            Human-readable sentiment label
        """
        label_mapping = {
            # Original model labels (fitsblb/YelpReviewsAnalyzer)
            "LABEL_0": "Negative",
            "LABEL_1": "Neutral", 
            "LABEL_2": "Positive",
            # Standard model labels (distilbert-base-uncased-finetuned-sst-2-english)
            "NEGATIVE": "Negative",
            "POSITIVE": "Positive",
            # Generic fallbacks
            "NEUTRAL": "Neutral"
        }
        
        mapped_label = label_mapping.get(label, "Unknown")
        
        if mapped_label == "Unknown":
            logger.warning(f"Unknown label received from model: {label}")
            # If it's an unknown label, try to infer from the label string
            label_lower = label.lower()
            if 'neg' in label_lower:
                mapped_label = "Negative"
            elif 'pos' in label_lower:
                mapped_label = "Positive"
            elif 'neu' in label_lower:
                mapped_label = "Neutral"
            else:
                mapped_label = "Neutral"  # Default fallback
        
        return mapped_label


# Global model instance
_sentiment_analyzer = None


def get_model() -> SentimentAnalyzer:
    """Get or create the global sentiment analyzer instance."""
    global _sentiment_analyzer
    
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    
    return _sentiment_analyzer


def predict(text: str) -> Tuple[str, float]:
    """
    Convenience function for sentiment prediction.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple of (sentiment_label, confidence_score)
        
    Raises:
        ModelError: If prediction fails
    """
    model = get_model()
    return model.predict(text)

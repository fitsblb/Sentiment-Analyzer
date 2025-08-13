"""
Unit tests for the model module.
Tests the sentiment analysis model functionality in isolation.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.model import SentimentAnalyzer, ModelError, predict, get_model


class TestSentimentAnalyzer:
    """Test cases for the SentimentAnalyzer class."""
    
    def test_sentiment_label_mapping_original_model(self):
        """Test label mapping for the original model labels."""
        analyzer = SentimentAnalyzer()
        
        # Test original model labels
        assert analyzer._map_sentiment_label("LABEL_0") == "Negative"
        assert analyzer._map_sentiment_label("LABEL_1") == "Neutral"
        assert analyzer._map_sentiment_label("LABEL_2") == "Positive"
    
    def test_sentiment_label_mapping_standard_model(self):
        """Test label mapping for standard model labels."""
        analyzer = SentimentAnalyzer()
        
        # Test standard model labels
        assert analyzer._map_sentiment_label("NEGATIVE") == "Negative"
        assert analyzer._map_sentiment_label("POSITIVE") == "Positive"
        assert analyzer._map_sentiment_label("NEUTRAL") == "Neutral"
    
    def test_sentiment_label_mapping_unknown_label(self):
        """Test handling of unknown labels."""
        analyzer = SentimentAnalyzer()
        
        # Test unknown labels with fallback logic
        assert analyzer._map_sentiment_label("UNKNOWN_LABEL") == "Neutral"
        assert analyzer._map_sentiment_label("SOME_NEG_LABEL") == "Negative"
        assert analyzer._map_sentiment_label("SOME_POS_LABEL") == "Positive"
        assert analyzer._map_sentiment_label("WEIRD_LABEL") == "Neutral"
    
    @patch('app.model.pipeline')
    def test_model_loading_success(self, mock_pipeline):
        """Test successful model loading."""
        # Mock successful pipeline creation
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.return_value = [{"label": "POSITIVE", "score": 0.9}]
        mock_pipeline.return_value = mock_pipeline_instance
        
        analyzer = SentimentAnalyzer()
        
        # Verify pipeline was called correctly
        mock_pipeline.assert_called_once()
        assert analyzer.pipeline is not None
    
    @patch('app.model.pipeline')
    def test_model_loading_with_fallback(self, mock_pipeline):
        """Test model loading with fallback when primary model fails."""
        # Mock primary model failure, then successful fallback
        mock_pipeline.side_effect = [
            Exception("Primary model failed"),  # First call fails
            MagicMock()  # Second call (fallback) succeeds
        ]
        
        # Mock the fallback pipeline
        mock_fallback = MagicMock()
        mock_fallback.return_value = [{"label": "POSITIVE", "score": 0.9}]
        mock_pipeline.side_effect[1] = mock_fallback
        
        analyzer = SentimentAnalyzer()
        
        # Verify fallback was used
        assert mock_pipeline.call_count == 2
        assert analyzer.model_name == "distilbert-base-uncased-finetuned-sst-2-english"
    
    @patch('app.model.pipeline')
    def test_model_loading_complete_failure(self, mock_pipeline):
        """Test model loading when both primary and fallback fail."""
        # Mock both primary and fallback failures
        mock_pipeline.side_effect = [
            Exception("Primary model failed"),
            Exception("Fallback model failed")
        ]
        
        with pytest.raises(ModelError):
            SentimentAnalyzer()
    
    def test_predict_with_mock_pipeline(self):
        """Test prediction with mocked pipeline."""
        analyzer = SentimentAnalyzer()
        
        # Mock the pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{"label": "POSITIVE", "score": 0.95}]
        analyzer.pipeline = mock_pipeline
        
        # Test prediction
        sentiment, confidence = analyzer.predict("This is great!")
        
        assert sentiment == "Positive"
        assert confidence == 0.95
        mock_pipeline.assert_called_once_with("This is great!")
    
    def test_predict_with_nested_list_response(self):
        """Test prediction handling nested list responses."""
        analyzer = SentimentAnalyzer()
        
        # Mock pipeline returning nested list
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [[{"label": "NEGATIVE", "score": 0.85}]]
        analyzer.pipeline = mock_pipeline
        
        sentiment, confidence = analyzer.predict("This is bad!")
        
        assert sentiment == "Negative"
        assert confidence == 0.85
    
    def test_predict_empty_response(self):
        """Test prediction with empty response."""
        analyzer = SentimentAnalyzer()
        
        # Mock empty response
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = []
        analyzer.pipeline = mock_pipeline
        
        with pytest.raises(ModelError):
            analyzer.predict("Test text")
    
    def test_predict_no_pipeline(self):
        """Test prediction when pipeline is not loaded."""
        analyzer = SentimentAnalyzer()
        analyzer.pipeline = None
        
        with pytest.raises(ModelError):
            analyzer.predict("Test text")


class TestModelFunctions:
    """Test cases for module-level functions."""
    
    @patch('app.model.SentimentAnalyzer')
    def test_get_model_singleton(self, mock_analyzer_class):
        """Test that get_model returns the same instance (singleton pattern)."""
        mock_instance = MagicMock()
        mock_analyzer_class.return_value = mock_instance
        
        # Call get_model multiple times
        model1 = get_model()
        model2 = get_model()
        
        # Should return the same instance
        assert model1 is model2
        # Analyzer should only be instantiated once
        mock_analyzer_class.assert_called_once()
    
    @patch('app.model.get_model')
    def test_predict_function(self, mock_get_model):
        """Test the module-level predict function."""
        # Mock the model
        mock_model = MagicMock()
        mock_model.predict.return_value = ("Positive", 0.9)
        mock_get_model.return_value = mock_model
        
        # Test predict function
        sentiment, confidence = predict("Great product!")
        
        assert sentiment == "Positive"
        assert confidence == 0.9
        mock_get_model.assert_called_once()
        mock_model.predict.assert_called_once_with("Great product!")


class TestModelErrorHandling:
    """Test cases for error handling scenarios."""
    
    def test_model_error_creation(self):
        """Test ModelError exception creation."""
        error = ModelError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    @patch('app.model.pipeline')
    def test_prediction_exception_handling(self, mock_pipeline):
        """Test prediction error handling."""
        analyzer = SentimentAnalyzer()
        
        # Mock pipeline that raises an exception during prediction
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.side_effect = Exception("Prediction failed")
        analyzer.pipeline = mock_pipeline_instance
        
        with pytest.raises(ModelError) as exc_info:
            analyzer.predict("Test text")
        
        assert "Sentiment prediction failed" in str(exc_info.value)

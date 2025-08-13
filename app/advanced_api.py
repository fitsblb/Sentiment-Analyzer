"""
Advanced API endpoints for sentiment analysis
Includes model comparison, batch processing, and analytics
"""

from flask import Blueprint, request, jsonify
from typing import List, Dict, Any
import logging
import time
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from advanced_model import get_advanced_analyzer, predict_advanced, predict_batch, get_model_stats
from config import config

logger = logging.getLogger('sentiment_analyzer.advanced_api')

# Create blueprint for advanced endpoints
advanced_bp = Blueprint('advanced', __name__, url_prefix='/api/v2')

@advanced_bp.route('/compare', methods=['POST'])
def compare_models():
    """Compare sentiment analysis across multiple models"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing required field: text',
                'status': 'error'
            }), 400
        
        text = data['text'].strip()
        if not text or len(text) > config.MAX_TEXT_LENGTH:
            return jsonify({
                'error': f'Text must be between 1 and {config.MAX_TEXT_LENGTH} characters',
                'status': 'error'
            }), 400
        
        # Get models to use (default to all available)
        models = data.get('models', None)
        
        # Perform comparison
        result = predict_advanced(text, models)
        
        # Format response
        response = {
            'status': 'success',
            'text': result.text,
            'consensus': {
                'sentiment': result.consensus_sentiment,
                'confidence': round(result.average_confidence, 4),
                'agreement_score': round(result.agreement_score, 4)
            },
            'model_results': [
                {
                    'model': r.model_name,
                    'sentiment': r.sentiment,
                    'confidence': round(r.confidence, 4),
                    'processing_time': round(r.processing_time, 4)
                }
                for r in result.results
            ],
            'processing_time': round(result.processing_time, 4),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Model comparison completed for text length {len(text)}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in model comparison: {e}")
        return jsonify({
            'error': 'Internal server error during model comparison',
            'status': 'error'
        }), 500

@advanced_bp.route('/batch', methods=['POST'])
def batch_analyze():
    """Analyze multiple texts in batch"""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({
                'error': 'Missing required field: texts (array)',
                'status': 'error'
            }), 400
        
        texts = data['texts']
        if not isinstance(texts, list):
            return jsonify({
                'error': 'Field "texts" must be an array',
                'status': 'error'
            }), 400
        
        if len(texts) == 0:
            return jsonify({
                'error': 'At least one text is required',
                'status': 'error'
            }), 400
        
        if len(texts) > 50:  # Limit batch size
            return jsonify({
                'error': 'Maximum 50 texts allowed per batch',
                'status': 'error'
            }), 400
        
        # Validate all texts
        for i, text in enumerate(texts):
            if not isinstance(text, str):
                return jsonify({
                    'error': f'Text at index {i} must be a string',
                    'status': 'error'
                }), 400
            
            if len(text.strip()) == 0 or len(text) > config.MAX_TEXT_LENGTH:
                return jsonify({
                    'error': f'Text at index {i} must be between 1 and {config.MAX_TEXT_LENGTH} characters',
                    'status': 'error'
                }), 400
        
        # Get model to use
        model_key = data.get('model', None)
        
        # Process batch
        start_time = time.time()
        results = predict_batch(texts, model_key)
        total_time = time.time() - start_time
        
        # Format response
        response = {
            'status': 'success',
            'batch_size': len(texts),
            'results': [
                {
                    'index': i,
                    'text': texts[i],
                    'sentiment': r.sentiment,
                    'confidence': round(r.confidence, 4),
                    'processing_time': round(r.processing_time, 4)
                }
                for i, r in enumerate(results)
            ],
            'total_processing_time': round(total_time, 4),
            'average_processing_time': round(total_time / len(texts), 4),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Batch analysis completed for {len(texts)} texts")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        return jsonify({
            'error': 'Internal server error during batch analysis',
            'status': 'error'
        }), 500

@advanced_bp.route('/models', methods=['GET'])
def get_models():
    """Get information about available models"""
    try:
        analyzer = get_advanced_analyzer()
        available_models = analyzer.get_available_models()
        performance_stats = get_model_stats()
        
        models_info = []
        for model_key in available_models:
            model_config = analyzer.model_configs[model_key]
            stats = performance_stats.get(model_key, {})
            
            models_info.append({
                'key': model_key,
                'name': model_config['name'],
                'supported_labels': list(model_config['label_mapping'].values()),
                'performance': {
                    'total_predictions': stats.get('total_predictions', 0),
                    'average_processing_time': round(stats.get('average_processing_time', 0), 4),
                    'error_rate': round(stats.get('error_rate', 0), 4),
                    'load_time': round(stats.get('load_time', 0), 4)
                }
            })
        
        response = {
            'status': 'success',
            'total_models': len(models_info),
            'models': models_info,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting models info: {e}")
        return jsonify({
            'error': 'Internal server error getting models information',
            'status': 'error'
        }), 500

@advanced_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get analytics and performance statistics"""
    try:
        performance_stats = get_model_stats()
        
        # Calculate overall statistics
        total_predictions = sum(stats.get('total_predictions', 0) for stats in performance_stats.values())
        total_errors = sum(stats.get('total_errors', 0) for stats in performance_stats.values())
        
        if total_predictions > 0:
            overall_error_rate = total_errors / (total_predictions + total_errors)
            avg_processing_time = sum(
                stats.get('average_processing_time', 0) * stats.get('total_predictions', 0)
                for stats in performance_stats.values()
            ) / total_predictions
        else:
            overall_error_rate = 0
            avg_processing_time = 0
        
        response = {
            'status': 'success',
            'overall_stats': {
                'total_predictions': total_predictions,
                'total_errors': total_errors,
                'overall_error_rate': round(overall_error_rate, 4),
                'average_processing_time': round(avg_processing_time, 4)
            },
            'model_performance': performance_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({
            'error': 'Internal server error getting analytics',
            'status': 'error'
        }), 500

@advanced_bp.route('/test-models', methods=['POST'])
def test_models():
    """Test all models with a sample text"""
    try:
        data = request.get_json()
        text = data.get('text', 'This is a test message for model comparison.')
        
        if len(text) > config.MAX_TEXT_LENGTH:
            return jsonify({
                'error': f'Text must not exceed {config.MAX_TEXT_LENGTH} characters',
                'status': 'error'
            }), 400
        
        # Test all models
        result = predict_advanced(text)
        
        response = {
            'status': 'success',
            'test_text': text,
            'results': {
                'consensus': {
                    'sentiment': result.consensus_sentiment,
                    'confidence': round(result.average_confidence, 4),
                    'agreement_score': round(result.agreement_score, 4)
                },
                'individual_models': [
                    {
                        'model': r.model_name,
                        'sentiment': r.sentiment,
                        'confidence': round(r.confidence, 4),
                        'processing_time': round(r.processing_time, 4),
                        'status': 'success' if r.sentiment != 'Error' else 'error'
                    }
                    for r in result.results
                ],
                'total_processing_time': round(result.processing_time, 4)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error testing models: {e}")
        return jsonify({
            'error': 'Internal server error testing models',
            'status': 'error'
        }), 500

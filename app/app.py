import os
import sys
import time
from flask import Flask, render_template, request, jsonify, abort
from werkzeug.exceptions import RequestEntityTooLarge, BadRequest

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from logging_config import get_logger
from model import predict, ModelError

# Initialize logger
logger = get_logger('app')

# Try to import advanced features
try:
    from advanced_api import advanced_bp
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced features not available: {e}")
    ADVANCED_FEATURES_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Register advanced API blueprint if available
if ADVANCED_FEATURES_AVAILABLE:
    app.register_blueprint(advanced_bp)
    logger.info("Advanced API endpoints registered")
else:
    logger.info("Running with basic features only")

# Log application startup
logger.info(f"Starting Sentiment Analyzer application in {os.getenv('FLASK_ENV', 'development')} mode")
logger.info(f"Using model: {config.MODEL_NAME}")


@app.before_request
def log_request_info():
    """Log incoming requests for monitoring and debugging."""
    start_time = time.time()
    request.start_time = start_time
    logger.debug(f"Request: {request.method} {request.url} from {request.remote_addr}")


@app.after_request
def log_response_info(response):
    """Log response information including processing time."""
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        logger.debug(f"Response: {response.status_code} for {request.method} {request.url} "
                    f"({duration:.3f}s)")
    return response


@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors with proper logging and user-friendly response."""
    logger.warning(f"Bad request from {request.remote_addr}: {error}")
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid input data. Please check your request format.'
        }), 400
    return render_template('error.html', 
                         error_code=400,
                         error_message="Invalid request. Please try again."), 400


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file/request too large errors."""
    logger.warning(f"Request too large from {request.remote_addr}")
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Request Too Large',
            'message': f'Text must be under {config.MAX_TEXT_LENGTH} characters.'
        }), 413
    return render_template('error.html',
                         error_code=413, 
                         error_message=f"Text is too long. Please keep it under {config.MAX_TEXT_LENGTH} characters."), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors with proper logging."""
    logger.error(f"Internal server error: {error}", exc_info=True)
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Something went wrong on our end. Please try again later.'
        }), 500
    return render_template('error.html',
                         error_code=500,
                         error_message="Something went wrong. Please try again later."), 500


def validate_text_input(text):
    """
    Validate text input for sentiment analysis.
    
    Args:
        text: Input text to validate
        
    Returns:
        str: Cleaned and validated text
        
    Raises:
        ValueError: If text is invalid
    """
    if not text or not isinstance(text, str):
        raise ValueError("Text input is required and must be a string")
    
    text = text.strip()
    if not text:
        raise ValueError("Text cannot be empty")
        
    if len(text) > config.MAX_TEXT_LENGTH:
        raise ValueError(f"Text must be under {config.MAX_TEXT_LENGTH} characters")
    
    # Basic content filtering (you can extend this)
    if len(text) < 3:
        raise ValueError("Text must be at least 3 characters long")
    
    return text


@app.route("/", methods=["GET", "POST"])
def home():
    """Main route for the web interface."""
    if request.method == "POST":
        try:
            user_input = request.form.get("text_input", "").strip()
            logger.info(f"Processing sentiment analysis request from web interface")
            
            # Validate input
            validated_text = validate_text_input(user_input)
            
            # Get prediction
            start_time = time.time()
            label, score = predict(validated_text)
            processing_time = time.time() - start_time
            
            logger.info(f"Sentiment analysis completed: {label} ({score:.3f}) in {processing_time:.3f}s")
            
            return render_template("result.html", 
                                 input_text=validated_text, 
                                 prediction=label, 
                                 confidence=score)
                                 
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return render_template('error.html',
                                 error_code=400,
                                 error_message=str(e)), 400
                                 
        except ModelError as e:
            logger.error(f"Model error: {e}")
            return render_template('error.html',
                                 error_code=500, 
                                 error_message="AI model is temporarily unavailable. Please try again later."), 500
                                 
        except Exception as e:
            logger.error(f"Unexpected error in home route: {e}", exc_info=True)
            return render_template('error.html',
                                 error_code=500,
                                 error_message="An unexpected error occurred. Please try again."), 500
    
    return render_template("home.html")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    REST API endpoint for sentiment analysis.
    
    Expected JSON input:
    {
        "text": "Text to analyze"
    }
    
    Returns JSON response:
    {
        "sentiment": "Positive|Neutral|Negative",
        "confidence": 0.95,
        "processing_time": 0.123
    }
    """
    try:
        if not request.is_json:
            logger.warning("API request without JSON content type")
            return jsonify({
                'error': 'Bad Request',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Bad Request', 
                'message': 'Empty JSON payload'
            }), 400
            
        text = data.get('text')
        logger.info(f"Processing API sentiment analysis request")
        
        # Validate input
        validated_text = validate_text_input(text)
        
        # Get prediction with timing
        start_time = time.time()
        label, score = predict(validated_text)
        processing_time = time.time() - start_time
        
        logger.info(f"API sentiment analysis completed: {label} ({score:.3f}) in {processing_time:.3f}s")
        
        return jsonify({
            'sentiment': label,
            'confidence': round(score, 4),
            'processing_time': round(processing_time, 3),
            'text_length': len(validated_text)
        })
        
    except ValueError as e:
        logger.warning(f"API validation error: {e}")
        return jsonify({
            'error': 'Validation Error',
            'message': str(e)
        }), 400
        
    except ModelError as e:
        logger.error(f"API model error: {e}")
        return jsonify({
            'error': 'Model Error',
            'message': 'AI model is temporarily unavailable'
        }), 503
        
    except Exception as e:
        logger.error(f"Unexpected API error: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring and load balancers."""
    try:
        # Quick model check with simple text
        predict("test")
        
        return jsonify({
            'status': 'healthy',
            'model': config.MODEL_NAME,
            'version': '1.0.0',
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 503


@app.route("/api/info", methods=["GET"])
def api_info():
    """API information endpoint."""
    endpoints = {
        'analyze': '/api/analyze',
        'health': '/api/health',
        'info': '/api/info'
    }
    
    # Add advanced endpoints if available
    if ADVANCED_FEATURES_AVAILABLE:
        endpoints.update({
            'compare_models': '/api/v2/compare',
            'batch_analyze': '/api/v2/batch',
            'models_info': '/api/v2/models',
            'analytics': '/api/v2/analytics',
            'test_models': '/api/v2/test-models'
        })
    
    return jsonify({
        'name': 'Sentiment Analyzer API',
        'version': '2.0.0' if ADVANCED_FEATURES_AVAILABLE else '1.0.0',
        'model': config.MODEL_NAME,
        'features': {
            'basic_analysis': True,
            'model_comparison': ADVANCED_FEATURES_AVAILABLE,
            'batch_processing': ADVANCED_FEATURES_AVAILABLE,
            'analytics': ADVANCED_FEATURES_AVAILABLE
        },
        'endpoints': endpoints,
        'limits': {
            'max_text_length': config.MAX_TEXT_LENGTH,
            'rate_limit': config.API_RATE_LIMIT,
            'max_batch_size': 50 if ADVANCED_FEATURES_AVAILABLE else 1
        }
    })


if __name__ == "__main__":
    # Get host and port from environment variables (for cloud deployment)
    host = os.getenv('HOST', config.HOST)
    port = int(os.getenv('PORT', config.PORT))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting {'development' if debug else 'production'} server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

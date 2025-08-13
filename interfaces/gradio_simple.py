import gradio as gr
import os
import sys

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try to import advanced model, fallback to basic if needed
try:
    from app.model import predict
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    
    # Try to load your custom model first
    try:
        MODEL_NAME = "fitsblb/YelpReviewsAnalyzer"
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
        CUSTOM_MODEL_AVAILABLE = True
    except:
        # Fallback to a general model
        sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        CUSTOM_MODEL_AVAILABLE = False
        
except ImportError:
    # Ultimate fallback
    from transformers import pipeline
    sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    CUSTOM_MODEL_AVAILABLE = False

def analyze_sentiment(text):
    """Analyze sentiment using available models"""
    if not text.strip():
        return "Please enter some text to analyze!"
    
    try:
        # Use the pipeline
        result = sentiment_pipeline(text)
        
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
        
        sentiment = result['label']
        confidence = result['score']
        
        # Map labels to consistent format
        if sentiment.upper() in ['POSITIVE', 'POS']:
            sentiment = "Positive"
        elif sentiment.upper() in ['NEGATIVE', 'NEG']:
            sentiment = "Negative"
        elif sentiment.upper() in ['NEUTRAL', 'NEU']:
            sentiment = "Neutral"
            
        model_info = "YelpReviewsAnalyzer (Custom)" if CUSTOM_MODEL_AVAILABLE else "RoBERTa (Fallback)"
        
        output = f"""
## 🎯 Sentiment Analysis Result
**Sentiment**: {sentiment}  
**Confidence**: {confidence:.3f}  
**Model**: {model_info}

---
*Analyzing sentiment with AI models*
        """
        return output
        
    except Exception as e:
        return f"❌ Error analyzing sentiment: {str(e)}"

# Create Gradio interface
demo = gr.Interface(
    fn=analyze_sentiment,
    inputs=gr.Textbox(
        label="📝 Enter Text for Sentiment Analysis",
        placeholder="Type your text here... (e.g., 'This restaurant has amazing food!')",
        lines=3
    ),
    outputs=gr.Markdown(label="🎯 Analysis Results"),
    title="🚀 Sentiment Analyzer",
    description="""
    **AI-Powered Sentiment Analysis**
    
    This system analyzes the sentiment of your text using transformer models.
    Enter any text and get instant sentiment predictions with confidence scores!
    """,
    examples=[
        ["This restaurant has absolutely amazing food and incredible service!"],
        ["The food was terrible and the service was slow."],
        ["It's an okay place, nothing special but not bad either."],
        ["I love this product! Best purchase I've ever made."],
        ["This movie was boring and way too long."]
    ],
    theme=gr.themes.Soft(),
    allow_flagging="never"
)

if __name__ == "__main__":
    demo.launch()

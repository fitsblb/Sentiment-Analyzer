import gradio as gr
import sys
import os

# Add the parent directory to Python path so we can import from app/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your advanced model system
try:
    from app.advanced_model import predict_advanced, get_advanced_analyzer
    ADVANCED_AVAILABLE = True
except ImportError:
    # Fallback to basic model if advanced isn't available
    from app.model import predict
    ADVANCED_AVAILABLE = False

def analyze_sentiment(text):
    """Analyze sentiment using the advanced multi-model system"""
    if not text.strip():
        return "Please enter some text to analyze!"
    
    try:
        if ADVANCED_AVAILABLE:
            # Use advanced multi-model system
            result = predict_advanced(text)
            
            # Format results for display
            model_results = []
            for model_result in result.results:
                model_results.append(f"**{model_result.model_name}**: {model_result.sentiment} ({model_result.confidence:.3f})")
            
            output = f"""
## 🎯 Consensus Result
**Sentiment**: {result.consensus_sentiment}  
**Confidence**: {result.average_confidence:.3f}  
**Agreement Score**: {result.agreement_score:.3f}  
**Processing Time**: {result.processing_time:.3f}s

## 🤖 Individual Model Results
{chr(10).join(model_results)}

---
*Powered by 4 AI models working together for superior accuracy!*
            """
            return output
        else:
            # Fallback to basic model
            sentiment, confidence = predict(text)
            return f"""
## 📊 Sentiment Analysis Result
**Sentiment**: {sentiment}  
**Confidence**: {confidence:.3f}

*Using YelpReviewsAnalyzer model*
            """
    
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
    title="🚀 Advanced Sentiment Analyzer",
    description="""
    **Multi-Model AI System for Superior Sentiment Analysis**
    
    This system uses up to 4 different AI models working together to provide more accurate sentiment predictions:
    - 🎯 YelpReviewsAnalyzer (custom fine-tuned model)
    - 🤖 DistilBERT (general-purpose)
    - 🐦 Twitter-RoBERTa (social media optimized)  
    - 💰 FinBERT (financial sentiment)
    
    The models vote on the final prediction using a consensus algorithm for higher accuracy!
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

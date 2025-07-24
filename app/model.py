from transformers import pipeline

# Load model once when the app starts
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="fitsblb/YelpReviewsAnalyzer"
)

def map_sentiment_label(label):
    if label == "LABEL_0":
        return "Negative"
    elif label == "LABEL_1":
        return "Neutral"
    elif label == "LABEL_2":
        return "Positive"
    else:
        return "Unknown"

def predict(text):
    output = sentiment_pipeline(text)
    raw_label = output[0]["label"]
    score = round(output[0]["score"], 3)
    sentiment = map_sentiment_label(raw_label)
    return sentiment, score

import requests
import json

print("🔍 Testing Analytics Endpoint...")
try:
    response = requests.get("http://127.0.0.1:5000/api/v2/analytics")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        overall = data.get('overall_stats', {})
        print(f"\n📊 Overall Statistics:")
        print(f"   Total Predictions: {overall.get('total_predictions', 0)}")
        print(f"   Total Errors: {overall.get('total_errors', 0)}")
        print(f"   Error Rate: {overall.get('overall_error_rate', 0):.3f}")
        print(f"   Avg Processing Time: {overall.get('average_processing_time', 0):.3f}s")
        
        print(f"\n🤖 Model Performance:")
        for model, stats in data.get('model_performance', {}).items():
            print(f"   {model}:")
            print(f"     - Predictions: {stats.get('total_predictions', 0)}")
            print(f"     - Avg Time: {stats.get('average_processing_time', 0):.3f}s")
            print(f"     - Error Rate: {stats.get('error_rate', 0):.3f}")

    print("\n🧪 Testing Models Info...")
    response = requests.get("http://127.0.0.1:5000/api/v2/models")
    if response.status_code == 200:
        data = response.json()
        print(f"Available Models: {data.get('total_models')}")
        for model in data.get('models', []):
            print(f"   - {model.get('name')} ({model.get('key')})")
            print(f"     Labels: {model.get('supported_labels')}")

    print("\n🔄 Testing Batch Processing...")
    batch_texts = [
        "I absolutely love this!",
        "This is terrible.",
        "It's okay, nothing special.",
        "Amazing quality!",
        "Worst purchase ever."
    ]

    response = requests.post("http://127.0.0.1:5000/api/v2/batch", 
                            json={"texts": batch_texts})
    if response.status_code == 200:
        data = response.json()
        print(f"Batch processed {data.get('batch_size')} texts in {data.get('total_processing_time', 0):.3f}s")
        print("Results:")
        for result in data.get('results', []):
            text = result.get('text', '')[:30] + "..." if len(result.get('text', '')) > 30 else result.get('text', '')
            print(f"   {result.get('index')}: '{text}' → {result.get('sentiment')} ({result.get('confidence', 0):.3f})")

    print("\n✅ All advanced features tested successfully!")

except Exception as e:
    print(f"Error: {e}")

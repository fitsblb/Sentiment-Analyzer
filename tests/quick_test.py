import requests
import json

try:
    # Test basic API info
    print("Testing API info...")
    response = requests.get("http://127.0.0.1:5000/api/info")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"API Version: {data.get('version')}")
        print(f"Advanced features: {data.get('features', {}).get('model_comparison', False)}")
        print(f"Available endpoints: {list(data.get('endpoints', {}).keys())}")
    
    # Test basic analysis
    print("\nTesting basic analysis...")
    response = requests.post("http://127.0.0.1:5000/api/analyze", 
                           json={"text": "This is amazing!"})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Sentiment: {data.get('sentiment')} (confidence: {data.get('confidence', 0):.3f})")
    
    # Test advanced model comparison
    print("\nTesting model comparison...")
    response = requests.post("http://127.0.0.1:5000/api/v2/compare", 
                           json={"text": "This product is fantastic!"})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        consensus = data.get('consensus', {})
        print(f"Consensus: {consensus.get('sentiment')} (confidence: {consensus.get('confidence', 0):.3f})")
        print(f"Agreement score: {consensus.get('agreement_score', 0):.3f}")
        print(f"Models tested: {len(data.get('model_results', []))}")
    
except Exception as e:
    print(f"Error: {e}")

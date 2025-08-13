"""
Test script for advanced sentiment analysis features
"""

try:
    print("Testing advanced model system...")
    
    from app.advanced_model import get_advanced_analyzer, predict_advanced
    print('✅ Advanced model imports successful')
    
    # Test getting analyzer
    analyzer = get_advanced_analyzer()
    available_models = analyzer.get_available_models()
    print(f'✅ Advanced analyzer created with {len(available_models)} models')
    print(f'   Available models: {available_models}')
    
    # Test prediction
    test_text = 'This is amazing! I love this product.'
    print(f'\nTesting with text: "{test_text}"')
    
    result = predict_advanced(test_text)
    print(f'✅ Advanced prediction successful!')
    print(f'   Consensus sentiment: {result.consensus_sentiment}')
    print(f'   Average confidence: {result.average_confidence:.3f}')
    print(f'   Agreement score: {result.agreement_score:.3f}')
    print(f'   Processing time: {result.processing_time:.3f}s')
    print(f'   Models tested: {len(result.results)}')
    
    print('\nIndividual model results:')
    for model_result in result.results:
        print(f'   {model_result.model_name}: {model_result.sentiment} '
              f'(confidence: {model_result.confidence:.3f}, '
              f'time: {model_result.processing_time:.3f}s)')
    
    print('\n✅ All tests passed!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

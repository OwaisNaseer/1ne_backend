"""Test script to analyze token usage and LLM response generation."""
import requests
import json

def test_execution_with_analysis():
    """Test execution and analyze token usage."""
    payload = {
        "data": {
            "subject": "science",
            "grade": 5,
            "topic": "Photosynthesis",
            "learning_objective": "Understand photosynthesis process",
            "time_duration": "50 min",
            "bloom_level": "Understand",
            "differentiation_needs": True
        }
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/templates/lesson_planner/execute",
        json=payload,
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    tokens = data.get('token_usage', {})
    
    print("=" * 60)
    print("TOKEN USAGE ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nModel: {data.get('model_used')}")
    print(f"Provider: {data.get('provider_used')}")
    print(f"Latency: {data.get('latency_ms')}ms")
    print(f"Cache Hit: {data.get('cache_hit', False)}")
    
    print("\n--- Token Breakdown ---")
    prompt_tokens = tokens.get('prompt', 0)
    completion_tokens = tokens.get('completion', 0)
    total_tokens = tokens.get('total', 0)
    
    print(f"Prompt Tokens: {prompt_tokens}")
    print(f"Completion Tokens: {completion_tokens}")
    print(f"Total Tokens: {total_tokens}")
    
    if total_tokens > 0:
        print(f"\nPrompt/Total Ratio: {prompt_tokens/total_tokens*100:.1f}%")
        print(f"Completion/Total Ratio: {completion_tokens/total_tokens*100:.1f}%")
    
    print("\n--- Cost Analysis ---")
    cost_estimate = data.get('cost_estimate')
    if cost_estimate is not None:
        print(f"Cost Estimate: ${cost_estimate:.6f}")
    else:
        print("Cost Estimate: None (not calculated)")
        # Calculate expected cost for gpt-4o-mini
        expected_cost = (prompt_tokens/1000 * 0.00015) + (completion_tokens/1000 * 0.0006)
        print(f"Expected Cost (gpt-4o-mini): ${expected_cost:.6f}")
    
    print("\n--- Output Quality Check ---")
    output = data.get('output', {})
    print(f"Has Overview: {bool(output.get('overview'))}")
    print(f"Learning Goals: {len(output.get('learning_goals', []))}")
    print(f"Steps: {len(output.get('steps', []))}")
    print(f"Materials: {len(output.get('materials', []))}")
    print(f"Teacher Notes: {len(output.get('teacher_notes', []))}")
    
    print("\n--- Token Efficiency Assessment ---")
    # Typical prompt for this type of request without TOON would be ~800-1200 tokens
    # With TOON, should be ~300-500 tokens
    if prompt_tokens < 500:
        print("✓ Prompt tokens are efficient (likely using TOON format)")
    elif prompt_tokens < 800:
        print("⚠ Prompt tokens are moderate (may not be using TOON optimally)")
    else:
        print("✗ Prompt tokens are high (TOON may not be working)")
    
    # Completion tokens for structured output should be ~200-400 for this type
    if completion_tokens < 400:
        print("✓ Completion tokens are reasonable")
    elif completion_tokens < 600:
        print("⚠ Completion tokens are moderate")
    else:
        print("✗ Completion tokens are high")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_execution_with_analysis()


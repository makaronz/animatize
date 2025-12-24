#!/usr/bin/env python3
"""
Test script for the Prompt Expander Module
Demonstrates usage and validates functionality
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.prompt_expander import PromptExpander, ExpansionRequest
import json
import time

def load_sample_rules():
    """Load sample cinematic rules for testing"""
    return [
        {
            "id": "rule_001",
            "name": "Establishing Shot",
            "snippet": "wide establishing shot setting the scene and mood",
            "priority": 0.9,
            "category": "composition"
        },
        {
            "id": "rule_003",
            "name": "Pan Following",
            "snippet": "smooth horizontal pan tracking movement",
            "priority": 0.8,
            "category": "camera_movement"
        },
        {
            "id": "rule_016",
            "name": "Golden Hour Lighting",
            "snippet": "warm golden hour light creating long shadows",
            "priority": 0.9,
            "category": "lighting"
        },
        {
            "id": "rule_025",
            "name": "Depth of Field",
            "snippet": "shallow depth of field isolating the subject",
            "priority": 0.7,
            "category": "technical"
        }
    ]

def test_basic_expansion():
    """Test basic prompt expansion functionality"""
    print("🎬 Testing Basic Prompt Expansion")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it as an environment variable.")
        print("   You can set it with: export OPENAI_API_KEY='your-key-here'")
        return False
    
    try:
        # Initialize the expander
        expander = PromptExpander(api_key=api_key)
        
        # Create test request
        rules = load_sample_rules()
        request = ExpansionRequest(
            base_prompt="A person walking through a city street",
            rules=rules,
            context={
                "time_of_day": "evening",
                "mood": "contemplative",
                "weather": "clear",
                "location_type": "urban"
            },
            max_tokens=400,
            temperature=0.7
        )
        
        print("📋 Test Request:")
        print(f"   Base Prompt: {request.base_prompt}")
        print(f"   Rules Applied: {len(request.rules)}")
        print(f"   Context: {request.context}")
        print()
        
        # Perform expansion
        print("🔄 Expanding prompt...")
        start_time = time.time()
        result = expander.expand_prompt(request)
        
        print("✅ Expansion Complete!")
        print(f"   Processing Time: {result.processing_time:.2f}s")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Tokens Used: {result.metadata.get('tokens_used', 'N/A')}")
        print(f"   Rules Applied: {', '.join(result.used_rules)}")
        print()
        
        print("📝 Expanded Prompt:")
        print("-" * 30)
        print(result.expanded_prompt)
        print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during expansion: {str(e)}")
        return False

def test_cache_functionality():
    """Test caching functionality"""
    print("\n🗄️ Testing Cache Functionality")
    print("=" * 50)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Skipping cache test - no API key")
        return
    
    try:
        expander = PromptExpander(api_key=api_key)
        
        # First call (should hit API)
        rules = load_sample_rules()[:2]  # Use fewer rules for cache test
        request = ExpansionRequest(
            base_prompt="A sunset over the ocean",
            rules=rules,
            max_tokens=300
        )
        
        print("🔄 First call (API request)...")
        start_time = time.time()
        result1 = expander.expand_prompt(request)
        first_call_time = time.time() - start_time
        
        print("🔄 Second call (should use cache)...")
        start_time = time.time()
        result2 = expander.expand_prompt(request)
        second_call_time = time.time() - start_time
        
        print(f"   First call time: {first_call_time:.2f}s")
        print(f"   Second call time: {second_call_time:.2f}s")
        print(f"   Cache stats: {expander.get_cache_stats()}")
        
        if second_call_time < first_call_time / 2:
            print("✅ Cache is working correctly")
        else:
            print("⚠️ Cache may not be functioning optimally")
            
    except Exception as e:
        print(f"❌ Error during cache test: {str(e)}")

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n🚨 Testing Error Handling")
    print("=" * 50)
    
    try:
        # Test with invalid API key
        expander = PromptExpander(api_key="invalid-key-12345")
        
        request = ExpansionRequest(
            base_prompt="Test prompt",
            rules=[{"id": "test", "name": "test", "snippet": "test rule", "priority": 0.5}]
        )
        
        # This should raise an exception
        result = expander.expand_prompt(request)
        print("❌ Should have failed with invalid API key")
        
    except Exception as e:
        print(f"✅ Correctly handled invalid API key: {type(e).__name__}")

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing Configuration")
    print("=" * 50)
    
    config_path = Path(__file__).parent.parent.parent / "configs" / "prompt_expander.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration file found")
        print(f"   Model: {config['model']}")
        print(f"   Max Tokens: {config['max_tokens']}")
        print(f"   Templates: {len(config['templates'])}")
    else:
        print("❌ Configuration file not found")

def main():
    """Run all tests"""
    print("🎯 ANIMAtiZE Prompt Expander Test Suite")
    print("=" * 60)
    
    # Run tests
    test_configuration()
    
    success = test_basic_expansion()
    test_cache_functionality()
    test_error_handling()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Prompt Expander Module is ready for use!")
        print("\nNext steps:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Import and use the PromptExpander class in your code")
        print("3. Check the examples in the documentation")
    else:
        print("❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
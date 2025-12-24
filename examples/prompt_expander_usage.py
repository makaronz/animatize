#!/usr/bin/env python3
"""
Prompt Expander Usage Example
Demonstrates how to use the ANIMAtiZE prompt expander module
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.prompt_expander import PromptExpander, ExpansionRequest
import json

def main():
    """Demonstrate prompt expander usage"""
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        return
    
    # Initialize the expander
    print("🎯 Initializing Prompt Expander...")
    expander = PromptExpander(api_key=api_key)
    
    # Load rules from the rules.json file
    rules_file = Path(__file__).parent.parent / "configs" / "rules" / "rules.json"
    if rules_file.exists():
        with open(rules_file, 'r') as f:
            all_rules = json.load(f)
            # Select a few rules for demonstration
            demo_rules = [
                all_rules["composition"][0],  # Rule of Thirds
                all_rules["lighting"][1],    # Golden Hour
                all_rules["camera_movement"][0],  # Pan Following
            ]
    else:
        # Fallback rules
        demo_rules = [
            {"id": "demo_001", "name": "Rule of Thirds", "snippet": "subject positioned according to rule of thirds", "priority": 0.8},
            {"id": "demo_002", "name": "Golden Hour", "snippet": "warm golden hour lighting with long shadows", "priority": 0.9},
        ]
    
    # Example 1: Basic prompt expansion
    print("\n🎬 Example 1: Basic Cinematic Expansion")
    print("-" * 40)
    
    request1 = ExpansionRequest(
        base_prompt="A woman standing on a cliff overlooking the ocean",
        rules=demo_rules,
        context={
            "time_of_day": "sunset",
            "mood": "contemplative",
            "weather": "clear",
            "style": "cinematic"
        },
        max_tokens=400,
        temperature=0.7
    )
    
    try:
        result1 = expander.expand_prompt(request1)
        print(f"✅ Expanded successfully!")
        print(f"   Confidence: {result1.confidence:.2f}")
        print(f"   Processing time: {result1.processing_time:.2f}s")
        print(f"   Rules applied: {len(result1.used_rules)}")
        print(f"\n📝 Expanded prompt:")
        print(result1.expanded_prompt)
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Action scene expansion
    print("\n🏃 Example 2: Action Scene Expansion")
    print("-" * 40)
    
    action_rules = [
        {"id": "action_001", "name": "Dynamic Tracking", "snippet": "fast-paced tracking shot following the action", "priority": 0.9},
        {"id": "action_002", "name": "Low Angle Power", "snippet": "low angle shot emphasizing power and dominance", "priority": 0.8},
    ]
    
    request2 = ExpansionRequest(
        base_prompt="A skateboarder performing tricks in an urban skate park",
        rules=action_rules,
        context={
            "time_of_day": "afternoon",
            "mood": "energetic",
            "location": "skate park"
        },
        max_tokens=350,
        temperature=0.8
    )
    
    try:
        result2 = expander.expand_prompt(request2)
        print(f"✅ Action scene expanded!")
        print(f"   Confidence: {result2.confidence:.2f}")
        print(f"   Processing time: {result2.processing_time:.2f}s")
        print(f"\n📝 Expanded prompt:")
        print(result2.expanded_prompt)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Display cache statistics
    print(f"\n📊 Cache Statistics: {expander.get_cache_stats()}")

if __name__ == "__main__":
    main()
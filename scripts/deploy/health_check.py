#!/usr/bin/env python3
"""
Health check script for ANIMAtiZE Framework
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def check_imports():
    """Check if all required modules can be imported"""
    try:
        import cv2
        import numpy
        import requests
        import openai
        from PIL import Image
        return True
    except ImportError as e:
        print(f"Import error: {e}", file=sys.stderr)
        return False

def check_directories():
    """Check if required directories exist"""
    required_dirs = ['data', 'logs', 'configs']
    base_path = Path(__file__).parent.parent.parent
    
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            print(f"Missing directory: {dir_path}", file=sys.stderr)
            return False
    return True

def check_environment():
    """Check if required environment variables are set"""
    # OPENAI_API_KEY is optional, so we just check if it's available
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("Warning: OPENAI_API_KEY not properly configured", file=sys.stderr)
        # Don't fail on this, just warn
    return True

def main():
    """Run all health checks"""
    checks = [
        ("Module imports", check_imports),
        ("Directory structure", check_directories),
        ("Environment variables", check_environment)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if check_func():
                print(f"✓ {check_name}")
            else:
                print(f"✗ {check_name}", file=sys.stderr)
                all_passed = False
        except Exception as e:
            print(f"✗ {check_name}: {e}", file=sys.stderr)
            all_passed = False
    
    if all_passed:
        print("\n✅ All health checks passed")
        sys.exit(0)
    else:
        print("\n❌ Some health checks failed", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

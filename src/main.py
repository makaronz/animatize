#!/usr/bin/env python3
"""
ANiMAtiZE Framework - Main Entry Point
"""

import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.framework import ANIMAtiZEFramework

async def main():
    """Main application entry point"""
    print("🎬 Starting ANIMAtiZE Framework...")
    
    framework = ANIMAtiZEFramework()
    await framework.initialize()
    
    print("✅ Framework initialized successfully!")
    print("🚀 Ready to generate cinematic prompts")

if __name__ == "__main__":
    asyncio.run(main())

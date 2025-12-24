#!/usr/bin/env python3
"""
Image Generator Usage Example
Demonstrates how to use the ANIMAtiZE image generation service
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.image_generator import ImageGenerator, GenerationRequest, ImageAPI

async def main():
    """Demonstrate image generator usage"""
    
    # Initialize the generator
    print("🎯 ANIMAtiZE Image Generator Demo")
    print("=" * 40)
    
    generator = ImageGenerator()
    
    # Check available APIs
    print("\n🔍 Available APIs:")
    apis = generator.get_supported_apis()
    for api in apis:
        status = "✅ Ready" if api["available"] else "❌ Needs API key"
        print(f"   {api['name'].upper()}: {status}")
    
    # Check cache stats
    cache_stats = generator.get_cache_stats()
    print(f"\n📊 Cache: {cache_stats['cached_images']} images, {cache_stats['cache_size_mb']:.1f} MB")
    
    # Example 1: Generate a cinematic scene
    print("\n🎬 Example 1: Cinematic Scene Generation")
    print("-" * 40)
    
    if os.getenv("OPENAI_API_KEY"):
        try:
            request = GenerationRequest(
                prompt="Epic cinematic shot of a lone warrior standing on a cliff overlooking a vast fantasy landscape at sunset, dramatic lighting, high fantasy art style",
                api=ImageAPI.DALLE,
                width=1024,
                height=1024,
                quality="high",
                style="cinematic"
            )
            
            print("🔄 Generating cinematic scene...")
            result = await generator.generate_image(request)
            
            # Save the image
            output_path = Path(__file__).parent.parent / "data" / "output" / "cinematic_scene.png"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(result.image_data)
            
            print(f"✅ Generated successfully!")
            print(f"   Quality score: {result.quality_score:.2f}")
            print(f"   Time taken: {result.generation_time:.2f}s")
            print(f"   Saved to: {output_path}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("   Skipping - no OpenAI API key")
    
    # Example 2: Generate with different quality settings
    print("\n🎨 Example 2: Quality Settings Comparison")
    print("-" * 40)
    
    if os.getenv("OPENAI_API_KEY"):
        qualities = ["standard", "hd"]
        
        for quality in qualities:
            try:
                request = GenerationRequest(
                    prompt="Minimalist modern architecture building, clean lines, geometric",
                    api=ImageAPI.DALLE,
                    width=512,
                    height=512,
                    quality=quality
                )
                
                print(f"🔄 Generating {quality} quality...")
                result = await generator.generate_image(request)
                
                output_path = Path(__file__).parent.parent / "data" / "output" / f"quality_{quality}.png"
                with open(output_path, 'wb') as f:
                    f.write(result.image_data)
                
                print(f"   {quality}: {len(result.image_data)/1024:.1f} KB")
                
            except Exception as e:
                print(f"   {quality}: Error - {e}")
    else:
        print("   Skipping - no OpenAI API key")
    
    # Example 3: Batch generation
    print("\n📦 Example 3: Batch Generation")
    print("-" * 40)
    
    if os.getenv("OPENAI_API_KEY"):
        try:
            requests = [
                GenerationRequest(
                    prompt="Serene mountain lake at sunrise, mirror reflections",
                    api=ImageAPI.DALLE,
                    width=512,
                    height=512
                ),
                GenerationRequest(
                    prompt="Futuristic city with flying cars and neon lights",
                    api=ImageAPI.DALLE,
                    width=512,
                    height=512
                ),
                GenerationRequest(
                    prompt="Mystical forest with ancient trees and magical light",
                    api=ImageAPI.DALLE,
                    width=512,
                    height=512
                )
            ]
            
            print("🔄 Generating batch of 3 images...")
            results = await generator.generate_batch(requests, max_concurrent=2)
            
            for i, result in enumerate(results):
                output_path = Path(__file__).parent.parent / "data" / "output" / f"batch_{i+1}.png"
                with open(output_path, 'wb') as f:
                    f.write(result.image_data)
                print(f"   Batch {i+1}: {result.quality_score:.2f} quality")
            
        except Exception as e:
            print(f"❌ Batch generation failed: {e}")
    else:
        print("   Skipping - no OpenAI API key")
    
    # Example 4: Cache demonstration
    print("\n🗄️ Example 4: Cache Performance")
    print("-" * 40)
    
    if os.getenv("OPENAI_API_KEY"):
        try:
            request = GenerationRequest(
                prompt="Simple geometric shapes on white background",
                api=ImageAPI.DALLE,
                width=256,
                height=256
            )
            
            # First call
            start_time = asyncio.get_event_loop().time()
            result1 = await generator.generate_image(request)
            time1 = asyncio.get_event_loop().time() - start_time
            
            # Second call (should be faster due to cache)
            start_time = asyncio.get_event_loop().time()
            result2 = await generator.generate_image(request)
            time2 = asyncio.get_event_loop().time() - start_time
            
            print(f"   First call: {time1:.2f}s")
            print(f"   Cached call: {time2:.2f}s")
            print(f"   Speed improvement: {((time1-time2)/time1)*100:.1f}%")
            
        except Exception as e:
            print(f"   Cache test failed: {e}")
    else:
        print("   Skipping - no OpenAI API key")
    
    # Final summary
    print("\n" + "=" * 40)
    print("📋 Usage Summary:")
    print("   1. Set API keys as environment variables:")
    print("      export OPENAI_API_KEY='your-key-here'")
    print("      export FLUX_API_KEY='your-key-here'")
    print("      export IMAGEN_API_KEY='your-key-here'")
    print("   2. Use ImageGenerator class for single images")
    print("   3. Use generate_batch for multiple images")
    print("   4. Check cache stats with get_cache_stats()")
    print("   5. Images saved to data/output/ directory")

if __name__ == "__main__":
    asyncio.run(main())
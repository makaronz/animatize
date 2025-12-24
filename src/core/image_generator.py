"""
Image Generation Module for ANIMAtiZE Framework
Handles integration with Flux and Imagen APIs for high-quality image generation
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import base64
from PIL import Image
import io
import time
from enum import Enum

class ImageAPI(Enum):
    """Supported image generation APIs"""
    FLUX = "flux"
    IMAGEN = "imagen"
    DALLE = "dalle"

@dataclass
class GenerationRequest:
    """Request structure for image generation"""
    prompt: str
    api: ImageAPI
    width: int = 1024
    height: int = 1024
    quality: str = "high"
    style: str = "cinematic"
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    guidance_scale: float = 7.5
    num_inference_steps: int = 50

@dataclass
class GenerationResult:
    """Result structure from image generation"""
    image_data: bytes
    api_used: ImageAPI
    generation_time: float
    metadata: Dict[str, Any]
    quality_score: float
    prompt_used: str

class ImageGenerator:
    """Multi-API image generation service"""
    
    def __init__(self):
        """Initialize the image generator with API configurations"""
        self.logger = logging.getLogger(__name__)
        
        # API configurations
        self.api_keys = {
            ImageAPI.FLUX: os.getenv("FLUX_API_KEY"),
            ImageAPI.IMAGEN: os.getenv("IMAGEN_API_KEY"),
            ImageAPI.DALLE: os.getenv("OPENAI_API_KEY")
        }
        
        self.api_endpoints = {
            ImageAPI.FLUX: "https://api.flux.ai/v1/generate",
            ImageAPI.IMAGEN: "https://imagen.googleapis.com/v1/images:generate",
            ImageAPI.DALLE: "https://api.openai.com/v1/images/generations"
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            "low": 0.6,
            "medium": 0.75,
            "high": 0.85,
            "ultra": 0.95
        }
        
        # Cache for generated images
        self.cache_dir = Path(__file__).parent.parent / "data" / "cache" / "images"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_image(self, request: GenerationRequest) -> GenerationResult:
        """Generate image using specified API"""
        start_time = time.time()
        
        # Check API key availability
        if not self.api_keys[request.api]:
            raise ValueError(f"API key not found for {request.api.value}")
        
        # Check cache first
        cached_result = await self._check_cache(request)
        if cached_result:
            self.logger.info("Returning cached image")
            return cached_result
        
        try:
            if request.api == ImageAPI.FLUX:
                result = await self._generate_flux(request)
            elif request.api == ImageAPI.IMAGEN:
                result = await self._generate_imagen(request)
            elif request.api == ImageAPI.DALLE:
                result = await self._generate_dalle(request)
            else:
                raise ValueError(f"Unsupported API: {request.api}")
            
            # Cache the result
            await self._cache_result(request, result)
            
            generation_time = time.time() - start_time
            self.logger.info(f"Image generated in {generation_time:.2f}s using {request.api.value}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating image with {request.api.value}: {str(e)}")
            raise
    
    async def _generate_flux(self, request: GenerationRequest) -> GenerationResult:
        """Generate image using Flux API"""
        headers = {
            "Authorization": f"Bearer {self.api_keys[ImageAPI.FLUX]}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": request.prompt,
            "width": request.width,
            "height": request.height,
            "num_inference_steps": request.num_inference_steps,
            "guidance_scale": request.guidance_scale,
            "seed": request.seed
        }
        
        if request.negative_prompt:
            payload["negative_prompt"] = request.negative_prompt
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_endpoints[ImageAPI.FLUX],
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"Flux API error: {response.status}")
                
                data = await response.json()
                image_data = base64.b64decode(data["images"][0])
                
                return GenerationResult(
                    image_data=image_data,
                    api_used=ImageAPI.FLUX,
                    generation_time=0.0,  # Will be calculated by caller
                    metadata={
                        "model": "flux-pro-1.1",
                        "seed": data.get("seed"),
                        "quality": request.quality
                    },
                    quality_score=await self._assess_quality(image_data),
                    prompt_used=request.prompt
                )
    
    async def _generate_imagen(self, request: GenerationRequest) -> GenerationResult:
        """Generate image using Google Imagen API"""
        headers = {
            "Authorization": f"Bearer {self.api_keys[ImageAPI.IMAGEN]}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "instances": [{
                "prompt": request.prompt,
                "parameters": {
                    "sampleCount": 1,
                    "sampleImageSize": f"{request.width}x{request.height}",
                    "aspectRatio": f"{request.width}:{request.height}",
                    "guidanceScale": request.guidance_scale,
                    "seed": request.seed
                }
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_endpoints[ImageAPI.IMAGEN],
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"Imagen API error: {response.status}")
                
                data = await response.json()
                image_data = base64.b64decode(data["predictions"][0]["bytesBase64Encoded"])
                
                return GenerationResult(
                    image_data=image_data,
                    api_used=ImageAPI.IMAGEN,
                    generation_time=0.0,
                    metadata={
                        "model": "imagen-3.0-generate-001",
                        "seed": data.get("parameters", {}).get("seed"),
                        "quality": request.quality
                    },
                    quality_score=await self._assess_quality(image_data),
                    prompt_used=request.prompt
                )
    
    async def _generate_dalle(self, request: GenerationRequest) -> GenerationResult:
        """Generate image using OpenAI DALL-E API"""
        headers = {
            "Authorization": f"Bearer {self.api_keys[ImageAPI.DALLE]}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": request.prompt,
            "n": 1,
            "size": f"{request.width}x{request.height}",
            "quality": request.quality,
            "style": request.style,
            "response_format": "b64_json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_endpoints[ImageAPI.DALLE],
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"DALL-E API error: {response.status}")
                
                data = await response.json()
                image_data = base64.b64decode(data["data"][0]["b64_json"])
                
                return GenerationResult(
                    image_data=image_data,
                    api_used=ImageAPI.DALLE,
                    generation_time=0.0,
                    metadata={
                        "model": "dall-e-3",
                        "revised_prompt": data["data"][0].get("revised_prompt"),
                        "quality": request.quality
                    },
                    quality_score=await self._assess_quality(image_data),
                    prompt_used=request.prompt
                )
    
    async def generate_batch(
        self, 
        requests: List[GenerationRequest],
        max_concurrent: int = 3
    ) -> List[GenerationResult]:
        """Generate multiple images concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(request):
            async with semaphore:
                return await self.generate_image(request)
        
        tasks = [generate_with_semaphore(request) for request in requests]
        return await asyncio.gather(*tasks)
    
    async def _check_cache(self, request: GenerationRequest) -> Optional[GenerationResult]:
        """Check if image exists in cache"""
        cache_key = self._generate_cache_key(request)
        cache_file = self.cache_dir / f"{cache_key}.png"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    image_data = f.read()
                
                return GenerationResult(
                    image_data=image_data,
                    api_used=request.api,
                    generation_time=0.0,
                    metadata={"cached": True},
                    quality_score=await self._assess_quality(image_data),
                    prompt_used=request.prompt
                )
            except Exception as e:
                self.logger.warning(f"Error reading cache: {str(e)}")
        
        return None
    
    async def _cache_result(self, request: GenerationRequest, result: GenerationResult):
        """Save generated image to cache"""
        cache_key = self._generate_cache_key(request)
        cache_file = self.cache_dir / f"{cache_key}.png"
        
        try:
            with open(cache_file, 'wb') as f:
                f.write(result.image_data)
        except Exception as e:
            self.logger.warning(f"Error caching image: {str(e)}")
    
    def _generate_cache_key(self, request: GenerationRequest) -> str:
        """Generate cache key for request"""
        key_data = {
            "prompt": request.prompt,
            "api": request.api.value,
            "width": request.width,
            "height": request.height,
            "quality": request.quality,
            "style": request.style,
            "seed": request.seed,
            "guidance_scale": request.guidance_scale
        }
        
        import hashlib
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _assess_quality(self, image_data: bytes) -> float:
        """Assess image quality using simple heuristics"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Basic quality metrics
            width, height = image.size
            total_pixels = width * height
            
            # Resolution score (higher is better)
            resolution_score = min(total_pixels / (1024 * 1024), 1.0)
            
            # Format detection
            format_score = 1.0 if image.format in ['PNG', 'JPEG', 'WEBP'] else 0.8
            
            # Combined quality score
            quality_score = (resolution_score + format_score) / 2
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            self.logger.warning(f"Error assessing quality: {str(e)}")
            return 0.5
    
    def get_supported_apis(self) -> List[str]:
        """Get list of supported APIs with availability status"""
        supported = []
        for api in ImageAPI:
            has_key = bool(self.api_keys[api])
            supported.append({
                "name": api.value,
                "available": has_key,
                "endpoint": self.api_endpoints[api]
            })
        return supported
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.png"))
        return {
            "cached_images": len(cache_files),
            "cache_size_mb": sum(f.stat().st_size for f in cache_files) / (1024 * 1024)
        }

# Example usage
async def main():
    """Example usage of the image generator"""
    import os
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    generator = ImageGenerator()
    
    # Check available APIs
    print("Available APIs:")
    for api_info in generator.get_supported_apis():
        status = "✅" if api_info["available"] else "❌"
        print(f"  {status} {api_info['name']}")
    
    # Generate a test image
    request = GenerationRequest(
        prompt="Cinematic shot of a lone figure on a mountain peak at sunset, dramatic lighting",
        api=ImageAPI.DALLE,
        width=1024,
        height=1024,
        quality="high",
        style="cinematic"
    )
    
    try:
        result = await generator.generate_image(request)
        print(f"\n✅ Image generated!")
        print(f"   API used: {result.api_used.value}")
        print(f"   Quality score: {result.quality_score:.2f}")
        print(f"   Generation time: {result.generation_time:.2f}s")
        print(f"   Image size: {len(result.image_data) / 1024:.1f} KB")
        
        # Save to file
        output_path = Path(__file__).parent.parent / "data" / "output" / "test_image.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(result.image_data)
        
        print(f"   Saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
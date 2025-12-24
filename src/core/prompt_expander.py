"""
Prompt Expander Module for ANIMAtiZE Framework
Handles GPT-based prompt expansion for cinematic rule application
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import openai
from openai import OpenAI
import time
from functools import lru_cache

@dataclass
class ExpansionRequest:
    """Request structure for prompt expansion"""
    base_prompt: str
    rules: List[Dict[str, Any]]
    context: Optional[Dict[str, Any]] = None
    max_tokens: int = 500
    temperature: float = 0.7

@dataclass
class ExpansionResult:
    """Result structure from prompt expansion"""
    expanded_prompt: str
    used_rules: List[str]
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]

class PromptExpander:
    """GPT-based prompt expansion service"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """Initialize the prompt expander with OpenAI API"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided or found in environment")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Load prompt templates
        self.templates_dir = Path(__file__).parent.parent / "configs" / "templates"
        self.templates = self._load_templates()
        
        # Initialize cache
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    def _load_templates(self) -> Dict[str, str]:
        """Load prompt templates from templates directory"""
        templates = {}
        template_files = [
            "base_expansion.txt",
            "cinematic_expansion.txt",
            "motion_prompt.txt",
            "composition_focus.txt"
        ]
        
        for template_file in template_files:
            template_path = self.templates_dir / template_file
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    templates[template_file.replace('.txt', '')] = f.read()
        
        return templates
    
    @lru_cache(maxsize=128)
    def _get_cache_key(self, request: ExpansionRequest) -> str:
        """Generate cache key for request"""
        rules_str = json.dumps(request.rules, sort_keys=True)
        context_str = json.dumps(request.context or {}, sort_keys=True)
        return f"{request.base_prompt}_{rules_str}_{context_str}"
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if result is cached and not expired"""
        if cache_key not in self.cache:
            return False
        
        timestamp, _ = self.cache[cache_key]
        return time.time() - timestamp < self.cache_ttl
    
    def _get_cached_result(self, cache_key: str) -> Optional[ExpansionResult]:
        """Get cached result if available"""
        if self._is_cached(cache_key):
            _, result = self.cache[cache_key]
            return result
        return None
    
    def _cache_result(self, cache_key: str, result: ExpansionResult):
        """Cache the expansion result"""
        self.cache[cache_key] = (time.time(), result)
    
    def expand_prompt(self, request: ExpansionRequest) -> ExpansionResult:
        """Expand a prompt using cinematic rules and GPT"""
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(request)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info("Returning cached result")
            return cached_result
        
        try:
            # Prepare the prompt
            system_prompt = self._build_system_prompt(request)
            user_prompt = self._build_user_prompt(request)
            
            # Make API call with retry logic
            response = self._call_openai_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            # Process response
            expanded_prompt = response.choices[0].message.content.strip()
            
            # Extract used rules
            used_rules = [rule['id'] for rule in request.rules]
            
            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(expanded_prompt, request.rules)
            
            result = ExpansionResult(
                expanded_prompt=expanded_prompt,
                used_rules=used_rules,
                confidence=confidence,
                processing_time=time.time() - start_time,
                metadata={
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens,
                    "cached": False
                }
            )
            
            # Cache the result
            self._cache_result(cache_key, result)
            
            self.logger.info(f"Prompt expansion completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Error expanding prompt: {str(e)}")
            raise
    
    def _build_system_prompt(self, request: ExpansionRequest) -> str:
        """Build system prompt for GPT"""
        base_template = self.templates.get("base_expansion", """
        You are an expert cinematographer and AI prompt engineer. Your task is to expand basic prompts into detailed, cinematic prompts using provided rules and context.
        
        Guidelines:
        - Maintain the original intent while adding cinematic depth
        - Apply relevant rules naturally without being mechanical
        - Focus on visual storytelling and emotional impact
        - Use specific, evocative language
        - Ensure technical accuracy in cinematography terms
        """)
        
        return base_template
    
    def _build_user_prompt(self, request: ExpansionRequest) -> str:
        """Build user prompt with rules and context"""
        rules_text = "\n".join([
            f"- {rule['name']}: {rule['snippet']} (priority: {rule['priority']})"
            for rule in request.rules
        ])
        
        context_text = ""
        if request.context:
            context_text = f"\nContext: {json.dumps(request.context, indent=2)}"
        
        prompt = f"""
        Base prompt: {request.base_prompt}
        
        Apply these cinematic rules:
        {rules_text}
        
        {context_text}
        
        Expand this into a detailed, cinematic prompt that incorporates the rules naturally while maintaining the original creative intent.
        """
        
        return prompt
    
    def _call_openai_with_retry(self, system_prompt: str, user_prompt: str, 
                               max_tokens: int, temperature: float, max_retries: int = 3) -> Any:
        """Call OpenAI API with retry logic"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=30
                )
                return response
                
            except openai.RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Rate limit hit, retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    raise
            
            except openai.APIError as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise
    
    def _calculate_confidence(self, expanded_prompt: str, rules: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on prompt quality"""
        
        # Simple heuristic-based confidence calculation
        confidence = 0.5  # Base confidence
        
        # Check for cinematic keywords
        cinematic_keywords = [
            "camera", "shot", "angle", "lighting", "composition", "depth", "focus",
            "movement", "tracking", "zoom", "pan", "tilt", "dolly", "crane"
        ]
        
        keyword_count = sum(1 for keyword in cinematic_keywords if keyword in expanded_prompt.lower())
        confidence += min(keyword_count * 0.05, 0.3)
        
        # Check for rule application
        rule_count = len(rules)
        confidence += min(rule_count * 0.02, 0.2)
        
        # Check for descriptive language
        descriptive_indicators = [
            "beautiful", "dramatic", "elegant", "smooth", "dynamic", "cinematic"
        ]
        
        descriptive_count = sum(1 for indicator in descriptive_indicators if indicator in expanded_prompt.lower())
        confidence += min(descriptive_count * 0.03, 0.15)
        
        return min(confidence, 1.0)
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        self.logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "cached_items": len(self.cache),
            "max_cache_size": 128,
            "cache_ttl": self.cache_ttl
        }

# Example usage and testing
if __name__ == "__main__":
    import os
    
    # Test the prompt expander
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        expander = PromptExpander(api_key=api_key)
        
        # Test expansion
        test_request = ExpansionRequest(
            base_prompt="A person walking through a city street",
            rules=[
                {"id": "rule_003", "name": "Pan Following", "snippet": "smooth horizontal pan tracking movement", "priority": 0.9},
                {"id": "rule_016", "name": "Golden Hour Lighting", "snippet": "warm golden hour light creating long shadows", "priority": 0.9}
            ],
            context={"time_of_day": "evening", "mood": "contemplative"}
        )
        
        result = expander.expand_prompt(test_request)
        print(f"Expanded: {result.expanded_prompt}")
        print(f"Confidence: {result.confidence}")
        print(f"Processing time: {result.processing_time}s")
    else:
        print("Please set OPENAI_API_KEY environment variable")
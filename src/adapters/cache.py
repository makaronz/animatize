from typing import Optional, Dict, Any
from dataclasses import dataclass
import hashlib
import json
import time
import threading
from collections import OrderedDict
from .contracts import UnifiedResponse


@dataclass
class CacheEntry:
    response: UnifiedResponse
    timestamp: float
    ttl: int
    access_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

    def update_access(self):
        self.access_count += 1
        self.last_accessed = time.time()


class CacheStrategy:
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"


class AdapterCache:
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        strategy: str = CacheStrategy.LRU,
        enable_stats: bool = True,
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        self.enable_stats = enable_stats

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()

        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired": 0,
            "invalidations": 0,
        }

    def generate_cache_key(
        self,
        provider: str,
        model: str,
        prompt: str,
        parameters: Dict[str, Any],
    ) -> str:
        params_str = json.dumps(parameters, sort_keys=True)
        params_hash = hashlib.sha256(params_str.encode()).hexdigest()[:16]
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        return f"{provider}:{model}:{prompt_hash}:{params_hash}"

    def get(self, cache_key: str) -> Optional[UnifiedResponse]:
        with self._lock:
            if cache_key not in self._cache:
                if self.enable_stats:
                    self._stats["misses"] += 1
                return None

            entry = self._cache[cache_key]

            if entry.is_expired():
                del self._cache[cache_key]
                if self.enable_stats:
                    self._stats["expired"] += 1
                    self._stats["misses"] += 1
                return None

            entry.update_access()

            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(cache_key)

            if self.enable_stats:
                self._stats["hits"] += 1

            return entry.response

    def set(
        self,
        cache_key: str,
        response: UnifiedResponse,
        ttl: Optional[int] = None,
    ):
        with self._lock:
            if ttl is None:
                ttl = self.default_ttl

            if len(self._cache) >= self.max_size:
                self._evict()

            entry = CacheEntry(
                response=response,
                timestamp=time.time(),
                ttl=ttl,
            )
            entry.update_access()

            self._cache[cache_key] = entry

            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(cache_key)

    def invalidate(self, cache_key: str) -> bool:
        with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
                if self.enable_stats:
                    self._stats["invalidations"] += 1
                return True
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        with self._lock:
            keys_to_delete = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self._cache[key]

            if self.enable_stats:
                self._stats["invalidations"] += len(keys_to_delete)

            return len(keys_to_delete)

    def invalidate_provider(self, provider: str) -> int:
        return self.invalidate_pattern(f"{provider}:")

    def invalidate_model(self, provider: str, model: str) -> int:
        return self.invalidate_pattern(f"{provider}:{model}:")

    def clear(self):
        with self._lock:
            self._cache.clear()
            if self.enable_stats:
                self._stats["invalidations"] += len(self._cache)

    def _evict(self):
        if not self._cache:
            return

        if self.strategy == CacheStrategy.LRU:
            self._cache.popitem(last=False)

        elif self.strategy == CacheStrategy.LFU:
            min_key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
            del self._cache[min_key]

        elif self.strategy == CacheStrategy.TTL:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].timestamp)
            del self._cache[oldest_key]

        if self.enable_stats:
            self._stats["evictions"] += 1

    def cleanup_expired(self) -> int:
        with self._lock:
            expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]

            for key in expired_keys:
                del self._cache[key]

            if self.enable_stats:
                self._stats["expired"] += len(expired_keys)

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": hit_rate,
                "evictions": self._stats["evictions"],
                "expired": self._stats["expired"],
                "invalidations": self._stats["invalidations"],
            }

    def reset_stats(self):
        with self._lock:
            self._stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
                "expired": 0,
                "invalidations": 0,
            }


class TieredCache:
    def __init__(
        self,
        l1_cache: AdapterCache,
        l2_cache: Optional[AdapterCache] = None,
    ):
        self.l1_cache = l1_cache
        self.l2_cache = l2_cache

    def get(self, cache_key: str) -> Optional[UnifiedResponse]:
        response = self.l1_cache.get(cache_key)

        if response is None and self.l2_cache:
            response = self.l2_cache.get(cache_key)
            if response:
                self.l1_cache.set(cache_key, response)

        return response

    def set(
        self,
        cache_key: str,
        response: UnifiedResponse,
        ttl: Optional[int] = None,
    ):
        self.l1_cache.set(cache_key, response, ttl)

        if self.l2_cache:
            self.l2_cache.set(cache_key, response, ttl)

    def invalidate(self, cache_key: str):
        self.l1_cache.invalidate(cache_key)
        if self.l2_cache:
            self.l2_cache.invalidate(cache_key)

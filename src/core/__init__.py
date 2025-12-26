"""
Core module initialization

Exports main classes and utilities from the core module.
"""

from .product_backlog import ProductBacklog, BacklogItem, Owner, Phase, RefactorType

from .video_pipeline import (
    VideoGenerationPipeline,
    PipelineConfig,
    PipelineMetrics,
    RetryConfig,
    RetryStrategy,
    FallbackChain,
)

__all__ = [
    "ProductBacklog",
    "BacklogItem",
    "Owner",
    "Phase",
    "RefactorType",
    "VideoGenerationPipeline",
    "PipelineConfig",
    "PipelineMetrics",
    "RetryConfig",
    "RetryStrategy",
    "FallbackChain",
]

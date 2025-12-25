"""
Core module initialization

Exports main classes and utilities from the core module.
"""

from .product_backlog import (
    ProductBacklog,
    BacklogItem,
    Owner,
    Phase,
    RefactorType
)

__all__ = [
    'ProductBacklog',
    'BacklogItem',
    'Owner',
    'Phase',
    'RefactorType'
]

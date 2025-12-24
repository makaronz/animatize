"""
ANIMAtiZE Wedge Features Module

This module contains the 8 strategic wedge features that create a defensible moat:
1. Film Grammar Engine
2. Shot List Compiler
3. Consistency Engine with Reference Management
4. Evaluation Harness with Golden Dataset
5. Temporal Control Layer
6. Automated Quality Assurance System
7. Character Identity Preservation Engine
8. Collaborative Production Workflow
"""

from .film_grammar import FilmGrammarEngine
from .shot_list_compiler import ShotListCompiler
from .consistency_engine import ConsistencyEngine, ReferenceManager
from .evaluation_harness import EvaluationHarness, GoldenDataset
from .temporal_control import TemporalControlLayer, KeyframeEditor
from .quality_assurance import QualityAssuranceSystem, QualityScorer
from .identity_preservation import CharacterIdentityEngine, IdentityTracker
from .collaborative_workflow import CollaborativeWorkflow, ProjectManager

__all__ = [
    'FilmGrammarEngine',
    'ShotListCompiler',
    'ConsistencyEngine',
    'ReferenceManager',
    'EvaluationHarness',
    'GoldenDataset',
    'TemporalControlLayer',
    'KeyframeEditor',
    'QualityAssuranceSystem',
    'QualityScorer',
    'CharacterIdentityEngine',
    'IdentityTracker',
    'CollaborativeWorkflow',
    'ProjectManager',
]

__version__ = '1.0.0'

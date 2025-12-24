"""
Film Grammar Engine - Wedge Feature #1

Creates proprietary knowledge base of cinematic language that improves with usage.
Provides defensible moat through data accumulation and expert validation.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class Genre(Enum):
    """Film genres with distinct cinematic conventions"""
    NEO_NOIR = "neo_noir"
    DOCUMENTARY = "documentary"
    COMMERCIAL = "commercial"
    ART_HOUSE = "art_house"
    ACTION = "action"
    DRAMA = "drama"
    COMEDY = "comedy"
    HORROR = "horror"
    ROMANCE = "romance"
    THRILLER = "thriller"
    SCI_FI = "sci_fi"
    WESTERN = "western"
    MUSICAL = "musical"
    ANIMATION = "animation"
    EXPERIMENTAL = "experimental"


class CulturalContext(Enum):
    """Cultural film traditions with unique grammar patterns"""
    HOLLYWOOD = "hollywood"
    EUROPEAN_ART = "european_art"
    JAPANESE = "japanese"
    KOREAN = "korean"
    BOLLYWOOD = "bollywood"
    FRENCH_NEW_WAVE = "french_new_wave"
    ITALIAN_NEOREALISM = "italian_neorealism"
    SOVIET_MONTAGE = "soviet_montage"


@dataclass
class GrammarRule:
    """Individual cinematic grammar rule"""
    rule_id: str
    name: str
    category: str
    description: str
    conditions: List[str]
    actions: List[str]
    justification: str
    examples: List[Dict]
    genre_applicability: List[Genre]
    cultural_context: List[CulturalContext]
    priority: float = 1.0
    confidence: float = 1.0
    usage_count: int = 0
    validation_score: float = 0.0
    expert_validated: bool = False
    metadata: Dict = field(default_factory=dict)


@dataclass
class GrammarValidation:
    """Validation result for grammar rule application"""
    rule_id: str
    is_valid: bool
    confidence: float
    violations: List[str]
    suggestions: List[str]
    alternative_rules: List[str]


class FilmGrammarEngine:
    """
    Film Grammar Engine - Strategic Wedge Feature
    
    Creates defensible moat through:
    - Proprietary film analysis corpus (10,000+ examples)
    - Rule evolution from director feedback
    - Automatic grammar validation
    - Cross-cultural cinematic patterns
    - Genre-specific movement libraries
    
    Measurement Metrics:
    - Grammar rule coverage: Target 95%+ of professional scenarios
    - Rule application accuracy: >92% match to director intent
    - Cross-genre adaptability: 15+ genre support
    - User satisfaction: NPS >50
    """
    
    def __init__(self, grammar_db_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.grammar_db_path = grammar_db_path or "data/film_grammar_db.json"
        self.rules: Dict[str, GrammarRule] = {}
        self.genre_rules: Dict[Genre, List[str]] = {}
        self.cultural_rules: Dict[CulturalContext, List[str]] = {}
        self.validation_history: List[GrammarValidation] = []
        
        self._load_grammar_database()
        self._initialize_indices()
    
    def _load_grammar_database(self):
        """Load grammar rules from database"""
        db_path = Path(self.grammar_db_path)
        if db_path.exists():
            try:
                with open(db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._deserialize_rules(data)
                self.logger.info(f"Loaded {len(self.rules)} grammar rules")
            except Exception as e:
                self.logger.error(f"Error loading grammar database: {e}")
                self._initialize_default_rules()
        else:
            self.logger.warning("Grammar database not found, initializing defaults")
            self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize with essential grammar rules"""
        default_rules = [
            GrammarRule(
                rule_id="FG_001",
                name="180-Degree Rule",
                category="camera_positioning",
                description="Maintain spatial relationships by keeping camera on one side of action axis",
                conditions=["scene_with_dialogue", "two_or_more_subjects"],
                actions=["establish_axis", "maintain_side"],
                justification="Preserves viewer orientation and spatial understanding",
                examples=[
                    {
                        "scenario": "conversation_between_two_people",
                        "correct": "camera stays on one side of imaginary line",
                        "violation": "crossing the line causes disorientation"
                    }
                ],
                genre_applicability=[Genre.DRAMA, Genre.ACTION, Genre.THRILLER],
                cultural_context=[CulturalContext.HOLLYWOOD, CulturalContext.EUROPEAN_ART],
                priority=1.0,
                expert_validated=True
            ),
            GrammarRule(
                rule_id="FG_002",
                name="Rule of Thirds Composition",
                category="composition",
                description="Place important elements along thirds grid intersections",
                conditions=["visual_scene", "key_subjects"],
                actions=["position_on_thirds", "balance_composition"],
                justification="Creates dynamic, balanced composition that guides viewer attention",
                examples=[
                    {
                        "scenario": "portrait_shot",
                        "technique": "eyes on upper third line",
                        "effect": "natural, professional framing"
                    }
                ],
                genre_applicability=[g for g in Genre],
                cultural_context=[c for c in CulturalContext],
                priority=0.9,
                expert_validated=True
            ),
            GrammarRule(
                rule_id="FG_003",
                name="Motivated Camera Movement",
                category="camera_movement",
                description="Camera moves must be justified by narrative or subject action",
                conditions=["dynamic_scene", "camera_motion"],
                actions=["link_to_subject", "follow_action", "reveal_information"],
                justification="Unmotivated camera movement breaks immersion",
                examples=[
                    {
                        "scenario": "character_walking",
                        "correct": "camera tracks with character",
                        "violation": "random pan during static dialogue"
                    }
                ],
                genre_applicability=[Genre.DRAMA, Genre.THRILLER, Genre.ACTION],
                cultural_context=[CulturalContext.HOLLYWOOD, CulturalContext.EUROPEAN_ART],
                priority=1.0,
                expert_validated=True
            ),
            GrammarRule(
                rule_id="FG_004",
                name="Eyeline Match",
                category="continuity",
                description="Character's gaze direction must match what they're looking at",
                conditions=["character_looking", "point_of_view_implied"],
                actions=["match_eyeline", "cut_to_pov"],
                justification="Establishes clear spatial relationships and subject focus",
                examples=[
                    {
                        "scenario": "character_looks_up",
                        "next_shot": "high_angle_shot_of_object",
                        "effect": "clear cause_and_effect"
                    }
                ],
                genre_applicability=[g for g in Genre],
                cultural_context=[CulturalContext.HOLLYWOOD, CulturalContext.BOLLYWOOD],
                priority=0.95,
                expert_validated=True
            ),
            GrammarRule(
                rule_id="FG_005",
                name="Establishing Shot",
                category="scene_structure",
                description="Begin sequence with wide shot showing spatial context",
                conditions=["new_location", "scene_start"],
                actions=["wide_shot", "show_geography", "establish_time"],
                justification="Orients viewer to space before detail shots",
                examples=[
                    {
                        "scenario": "new_scene_interior",
                        "technique": "wide_shot_showing_room_layout",
                        "progression": "then_move_to_closer_shots"
                    }
                ],
                genre_applicability=[Genre.DRAMA, Genre.ACTION, Genre.THRILLER, Genre.DOCUMENTARY],
                cultural_context=[c for c in CulturalContext],
                priority=0.85,
                expert_validated=True
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
    
    def _initialize_indices(self):
        """Build indices for fast rule lookup"""
        self.genre_rules.clear()
        self.cultural_rules.clear()
        
        for rule_id, rule in self.rules.items():
            for genre in rule.genre_applicability:
                if genre not in self.genre_rules:
                    self.genre_rules[genre] = []
                self.genre_rules[genre].append(rule_id)
            
            for context in rule.cultural_context:
                if context not in self.cultural_rules:
                    self.cultural_rules[context] = []
                self.cultural_rules[context].append(rule_id)
    
    def get_applicable_rules(
        self,
        genre: Optional[Genre] = None,
        cultural_context: Optional[CulturalContext] = None,
        category: Optional[str] = None,
        min_priority: float = 0.0
    ) -> List[GrammarRule]:
        """Get rules applicable to specific context"""
        candidate_rules = set()
        
        if genre:
            candidate_rules.update(self.genre_rules.get(genre, []))
        
        if cultural_context:
            cultural_set = set(self.cultural_rules.get(cultural_context, []))
            if candidate_rules:
                candidate_rules &= cultural_set
            else:
                candidate_rules = cultural_set
        
        if not candidate_rules:
            candidate_rules = set(self.rules.keys())
        
        applicable = [
            self.rules[rule_id]
            for rule_id in candidate_rules
            if self.rules[rule_id].priority >= min_priority
        ]
        
        if category:
            applicable = [r for r in applicable if r.category == category]
        
        return sorted(applicable, key=lambda r: r.priority, reverse=True)
    
    def validate_grammar(
        self,
        scene_description: Dict,
        applied_rules: List[str],
        strict_mode: bool = False
    ) -> GrammarValidation:
        """Validate grammar rule application for a scene"""
        violations = []
        suggestions = []
        alternative_rules = []
        confidence_scores = []
        
        for rule_id in applied_rules:
            if rule_id not in self.rules:
                violations.append(f"Unknown rule: {rule_id}")
                continue
            
            rule = self.rules[rule_id]
            
            conditions_met = self._evaluate_conditions(
                rule.conditions,
                scene_description
            )
            
            if not conditions_met:
                violations.append(
                    f"Rule {rule_id} conditions not met: {rule.conditions}"
                )
                suggestions.append(
                    f"Consider rules: {self._suggest_alternative_rules(scene_description)}"
                )
            else:
                confidence_scores.append(rule.confidence)
                rule.usage_count += 1
        
        essential_rules = self._get_essential_rules(scene_description)
        missing_essential = set(essential_rules) - set(applied_rules)
        
        if missing_essential:
            for rule_id in missing_essential:
                suggestions.append(
                    f"Consider applying essential rule: {rule_id} - {self.rules[rule_id].name}"
                )
                alternative_rules.append(rule_id)
        
        is_valid = len(violations) == 0 if strict_mode else len(violations) < 3
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        validation = GrammarValidation(
            rule_id=",".join(applied_rules),
            is_valid=is_valid,
            confidence=float(avg_confidence),
            violations=violations,
            suggestions=suggestions,
            alternative_rules=alternative_rules
        )
        
        self.validation_history.append(validation)
        return validation
    
    def _evaluate_conditions(self, conditions: List[str], scene_description: Dict) -> bool:
        """Evaluate if scene meets rule conditions"""
        scene_tags = scene_description.get('tags', [])
        scene_type = scene_description.get('type', '')
        
        for condition in conditions:
            if condition in scene_tags or condition == scene_type:
                continue
            
            if condition.startswith('has_'):
                element = condition[4:]
                if element not in scene_description.get('elements', []):
                    return False
            else:
                return False
        
        return True
    
    def _get_essential_rules(self, scene_description: Dict) -> List[str]:
        """Identify essential rules for scene type"""
        essential = []
        scene_type = scene_description.get('type', '')
        
        if 'dialogue' in scene_type:
            essential.append('FG_001')
            essential.append('FG_004')
        
        if 'new_location' in scene_description.get('tags', []):
            essential.append('FG_005')
        
        if 'camera_movement' in scene_description.get('elements', []):
            essential.append('FG_003')
        
        return essential
    
    def _suggest_alternative_rules(self, scene_description: Dict) -> List[str]:
        """Suggest alternative rules for scene"""
        category = scene_description.get('category', 'general')
        
        candidates = [
            rule_id for rule_id, rule in self.rules.items()
            if rule.category == category or category in rule.description.lower()
        ]
        
        return candidates[:3]
    
    def learn_from_feedback(self, rule_id: str, feedback: Dict) -> bool:
        """Update rule based on user feedback"""
        if rule_id not in self.rules:
            return False
        
        rule = self.rules[rule_id]
        rating = feedback.get('rating', 0)
        
        if rating > 0:
            current_weight = rule.usage_count
            new_confidence = (rule.confidence * current_weight + rating) / (current_weight + 1)
            rule.confidence = new_confidence
            rule.validation_score = (rule.validation_score * current_weight + rating) / (current_weight + 1)
        
        if feedback.get('corrections'):
            if 'corrections' not in rule.metadata:
                rule.metadata['corrections'] = []
            rule.metadata['corrections'].append(feedback['corrections'])
        
        return True
    
    def get_coverage_stats(self) -> Dict:
        """Get grammar coverage statistics"""
        total_rules = len(self.rules)
        validated_rules = sum(1 for r in self.rules.values() if r.expert_validated)
        
        return {
            'total_rules': total_rules,
            'validated_rules': validated_rules,
            'validation_rate': validated_rules / total_rules if total_rules > 0 else 0,
            'genre_coverage': {g.value: len(rules) for g, rules in self.genre_rules.items()},
            'cultural_coverage': {c.value: len(rules) for c, rules in self.cultural_rules.items()},
            'avg_confidence': float(np.mean([r.confidence for r in self.rules.values()])),
            'total_usage': sum(r.usage_count for r in self.rules.values())
        }
    
    def save_database(self, path: Optional[str] = None) -> bool:
        """Save grammar database to file"""
        save_path = path or self.grammar_db_path
        
        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'version': '1.0.0',
                'rules': {
                    rule_id: {
                        'rule_id': rule.rule_id,
                        'name': rule.name,
                        'category': rule.category,
                        'description': rule.description,
                        'conditions': rule.conditions,
                        'actions': rule.actions,
                        'justification': rule.justification,
                        'examples': rule.examples,
                        'genre_applicability': [g.value for g in rule.genre_applicability],
                        'cultural_context': [c.value for c in rule.cultural_context],
                        'priority': rule.priority,
                        'confidence': rule.confidence,
                        'usage_count': rule.usage_count,
                        'validation_score': rule.validation_score,
                        'expert_validated': rule.expert_validated,
                        'metadata': rule.metadata
                    }
                    for rule_id, rule in self.rules.items()
                }
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving grammar database: {e}")
            return False
    
    def _deserialize_rules(self, data: Dict):
        """Deserialize rules from JSON data"""
        for rule_id, rule_data in data.get('rules', {}).items():
            rule = GrammarRule(
                rule_id=rule_data['rule_id'],
                name=rule_data['name'],
                category=rule_data['category'],
                description=rule_data['description'],
                conditions=rule_data['conditions'],
                actions=rule_data['actions'],
                justification=rule_data['justification'],
                examples=rule_data['examples'],
                genre_applicability=[Genre(g) for g in rule_data['genre_applicability']],
                cultural_context=[CulturalContext(c) for c in rule_data['cultural_context']],
                priority=rule_data.get('priority', 1.0),
                confidence=rule_data.get('confidence', 1.0),
                usage_count=rule_data.get('usage_count', 0),
                validation_score=rule_data.get('validation_score', 0.0),
                expert_validated=rule_data.get('expert_validated', False),
                metadata=rule_data.get('metadata', {})
            )
            self.rules[rule_id] = rule

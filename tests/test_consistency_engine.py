"""
Unit tests for Consistency Engine

Tests:
1. Reference management (character_ref, style_anchors, embeddings)
2. Continuity rules (color consistency, lighting continuity, spatial coherence)
3. Scene analyzer integration and style extraction
4. Reference library storage and retrieval
5. Cross-shot consistency validation
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np
import json

from src.wedge_features.consistency_engine import (
    ConsistencyEngine,
    ReferenceLibrary,
    ReferenceManager,
    StyleAnchor,
    CharacterReference,
    WorldReference,
    ReferenceFrame,
    ConsistencyType,
    ConsistencyViolation,
    ColorConsistencyRule,
    LightingContinuityRule,
    SpatialCoherenceRule,
    StyleExtractor,
    CrossShotValidator,
)


class TestStyleAnchor(unittest.TestCase):
    """Test StyleAnchor class"""

    def test_style_anchor_creation(self):
        """Test creating a style anchor"""
        embedding = np.random.rand(64).astype(np.float32)
        
        style = StyleAnchor(
            anchor_id="test_style_01",
            name="Test Style",
            description="A test style anchor",
            style_embedding=embedding,
            color_palette=[(255, 0, 0), (0, 255, 0), (0, 0, 255)],
        )
        
        self.assertEqual(style.anchor_id, "test_style_01")
        self.assertEqual(style.name, "Test Style")
        self.assertEqual(len(style.color_palette), 3)
        self.assertEqual(style.style_embedding.shape, (64,))

    def test_style_anchor_serialization(self):
        """Test style anchor to/from dict"""
        embedding = np.random.rand(64).astype(np.float32)
        
        style = StyleAnchor(
            anchor_id="test_style_01",
            name="Test Style",
            description="A test style anchor",
            style_embedding=embedding,
            color_palette=[(255, 0, 0)],
        )
        
        style_dict = style.to_dict()
        self.assertIn("anchor_id", style_dict)
        self.assertIn("style_embedding", style_dict)
        
        style_restored = StyleAnchor.from_dict(style_dict)
        self.assertEqual(style_restored.anchor_id, style.anchor_id)
        np.testing.assert_array_almost_equal(style_restored.style_embedding, style.style_embedding)


class TestCharacterReference(unittest.TestCase):
    """Test CharacterReference class"""

    def test_character_reference_creation(self):
        """Test creating a character reference"""
        embedding = np.random.rand(64).astype(np.float32)
        
        character = CharacterReference(
            character_id="hero_001",
            name="Hero",
            description="Main character",
            appearance_embedding=embedding,
            facial_features={"eye_color": "blue"},
            body_proportions={"height": 1.8},
        )
        
        self.assertEqual(character.character_id, "hero_001")
        self.assertEqual(character.name, "Hero")
        self.assertEqual(character.facial_features["eye_color"], "blue")

    def test_character_reference_serialization(self):
        """Test character reference to/from dict"""
        embedding = np.random.rand(64).astype(np.float32)
        expression_variants = {"smile": np.random.rand(64).astype(np.float32)}
        
        character = CharacterReference(
            character_id="hero_001",
            name="Hero",
            description="Main character",
            appearance_embedding=embedding,
            expression_variants=expression_variants,
        )
        
        char_dict = character.to_dict()
        char_restored = CharacterReference.from_dict(char_dict)
        
        self.assertEqual(char_restored.character_id, character.character_id)
        np.testing.assert_array_almost_equal(
            char_restored.appearance_embedding, character.appearance_embedding
        )
        np.testing.assert_array_almost_equal(
            char_restored.expression_variants["smile"], expression_variants["smile"]
        )


class TestWorldReference(unittest.TestCase):
    """Test WorldReference class"""

    def test_world_reference_creation(self):
        """Test creating a world reference"""
        embedding = np.random.rand(64).astype(np.float32)
        
        world = WorldReference(
            world_id="castle_01",
            name="Grand Castle",
            description="A majestic castle",
            spatial_embedding=embedding,
            location_map={"gate": (0.5, 0.5, 0.0)},
            time_of_day="midday",
        )
        
        self.assertEqual(world.world_id, "castle_01")
        self.assertEqual(world.time_of_day, "midday")
        self.assertIn("gate", world.location_map)


class TestReferenceFrame(unittest.TestCase):
    """Test ReferenceFrame class"""

    def test_reference_frame_creation(self):
        """Test creating a reference frame"""
        frame = ReferenceFrame(
            frame_id="frame_001",
            shot_id="shot_001",
            timestamp=0.5,
            embeddings={"style": np.random.rand(64).astype(np.float32)},
            color_histogram=np.array([0.3, 0.2, 0.15, 0.1]),
            lighting_profile={"intensity": 0.75},
            character_positions={"hero": (0.5, 0.6)},
        )
        
        self.assertEqual(frame.frame_id, "frame_001")
        self.assertEqual(frame.shot_id, "shot_001")
        self.assertEqual(frame.timestamp, 0.5)
        self.assertIn("style", frame.embeddings)

    def test_reference_frame_serialization(self):
        """Test reference frame to/from dict"""
        frame = ReferenceFrame(
            frame_id="frame_001",
            shot_id="shot_001",
            timestamp=0.5,
            embeddings={"style": np.random.rand(64).astype(np.float32)},
            character_ids={"hero_001", "villain_001"},
        )
        
        frame_dict = frame.to_dict()
        frame_restored = ReferenceFrame.from_dict(frame_dict)
        
        self.assertEqual(frame_restored.frame_id, frame.frame_id)
        self.assertEqual(frame_restored.character_ids, frame.character_ids)


class TestContinuityRules(unittest.TestCase):
    """Test continuity rules"""

    def test_color_consistency_rule(self):
        """Test color consistency rule"""
        rule = ColorConsistencyRule(threshold=0.1)
        
        frame_a = ReferenceFrame(
            frame_id="frame_a",
            shot_id="shot_001",
            timestamp=0.0,
            color_histogram=np.array([0.3, 0.2, 0.15, 0.1]),
        )
        
        frame_b = ReferenceFrame(
            frame_id="frame_b",
            shot_id="shot_001",
            timestamp=0.5,
            color_histogram=np.array([0.3, 0.2, 0.15, 0.1]),
        )
        
        score = rule.evaluate(frame_a, frame_b)
        self.assertIsNotNone(score)
        self.assertGreater(score, 0.9)

    def test_lighting_continuity_rule(self):
        """Test lighting continuity rule"""
        rule = LightingContinuityRule(threshold=0.15)
        
        frame_a = ReferenceFrame(
            frame_id="frame_a",
            shot_id="shot_001",
            timestamp=0.0,
            lighting_profile={"intensity": 0.75, "color_temperature": 5500},
        )
        
        frame_b = ReferenceFrame(
            frame_id="frame_b",
            shot_id="shot_001",
            timestamp=0.5,
            lighting_profile={"intensity": 0.76, "color_temperature": 5500},
        )
        
        score = rule.evaluate(frame_a, frame_b)
        self.assertIsNotNone(score)
        self.assertGreater(score, 0.8)

    def test_spatial_coherence_rule(self):
        """Test spatial coherence rule"""
        rule = SpatialCoherenceRule(threshold=0.2)
        
        frame_a = ReferenceFrame(
            frame_id="frame_a",
            shot_id="shot_001",
            timestamp=0.0,
            character_positions={"hero": (0.5, 0.6)},
        )
        
        frame_b = ReferenceFrame(
            frame_id="frame_b",
            shot_id="shot_001",
            timestamp=0.5,
            character_positions={"hero": (0.52, 0.61)},
        )
        
        score = rule.evaluate(frame_a, frame_b)
        self.assertIsNotNone(score)
        self.assertGreater(score, 0.9)


class TestReferenceLibrary(unittest.TestCase):
    """Test ReferenceLibrary class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.library = ReferenceLibrary(storage_path=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    def test_add_character(self):
        """Test adding character to library"""
        character = CharacterReference(
            character_id="test_char",
            name="Test Character",
            description="A test character",
            appearance_embedding=np.random.rand(64).astype(np.float32),
        )
        
        success = self.library.add_character(character)
        self.assertTrue(success)
        
        retrieved = self.library.get_character("test_char")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Character")

    def test_add_style_anchor(self):
        """Test adding style anchor to library"""
        style = StyleAnchor(
            anchor_id="test_style",
            name="Test Style",
            description="A test style",
            style_embedding=np.random.rand(64).astype(np.float32),
        )
        
        success = self.library.add_style_anchor(style)
        self.assertTrue(success)
        
        retrieved = self.library.get_style("test_style")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Style")

    def test_add_world(self):
        """Test adding world to library"""
        world = WorldReference(
            world_id="test_world",
            name="Test World",
            description="A test world",
            spatial_embedding=np.random.rand(64).astype(np.float32),
        )
        
        success = self.library.add_world(world)
        self.assertTrue(success)
        
        retrieved = self.library.get_world("test_world")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test World")

    def test_find_similar_characters(self):
        """Test finding similar characters"""
        char1 = CharacterReference(
            character_id="char1",
            name="Character 1",
            description="First character",
            appearance_embedding=np.array([1.0] * 64, dtype=np.float32),
        )
        
        char2 = CharacterReference(
            character_id="char2",
            name="Character 2",
            description="Second character",
            appearance_embedding=np.array([0.0] * 64, dtype=np.float32),
        )
        
        self.library.add_character(char1)
        self.library.add_character(char2)
        
        query = np.array([0.9] * 64, dtype=np.float32)
        similar = self.library.find_similar_characters(query, top_k=2)
        
        self.assertEqual(len(similar), 2)
        self.assertEqual(similar[0][0], "char1")


class TestStyleExtractor(unittest.TestCase):
    """Test StyleExtractor class"""

    def test_create_style_embedding(self):
        """Test creating style embedding"""
        extractor = StyleExtractor()
        
        style_features = {
            "color_palette": [(255, 0, 0), (0, 255, 0)],
            "lighting_style": {"intensity": "medium"},
            "texture_profile": {"complexity": 0.5, "smoothness": 0.7},
            "composition_style": {"edge_density": 0.1},
        }
        
        embedding = extractor.create_style_embedding(style_features)
        
        self.assertEqual(embedding.shape, (64,))
        self.assertEqual(embedding.dtype, np.float32)

    def test_extract_style_from_analysis(self):
        """Test extracting style from scene analysis"""
        extractor = StyleExtractor()
        
        scene_analysis = {
            "scene_type": {
                "type": "landscape",
                "color_ratios": {
                    "sky": 0.4,
                    "vegetation": 0.3,
                    "building": 0.1,
                    "water": 0.2,
                },
            },
            "composition": {
                "symmetry": {"horizontal_symmetry": 0.8, "vertical_symmetry": 0.5},
                "complexity": {"edge_density": 0.15, "texture_complexity": 0.6},
            },
            "image_info": {"mean_brightness": 150},
        }
        
        style_features = extractor.extract_style_from_analysis(scene_analysis)
        
        self.assertIn("color_palette", style_features)
        self.assertIn("composition_style", style_features)
        self.assertIn("lighting_style", style_features)
        self.assertIn("texture_profile", style_features)


class TestCrossShotValidator(unittest.TestCase):
    """Test CrossShotValidator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.library = ReferenceLibrary(storage_path=self.temp_dir)
        self.validator = CrossShotValidator(self.library)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    def test_validate_shot_sequence(self):
        """Test validating shot sequence"""
        frames = [
            ReferenceFrame(
                frame_id=f"frame_{i}",
                shot_id="shot_001",
                timestamp=i * 0.5,
                color_histogram=np.array([0.3, 0.2, 0.15, 0.1]),
                lighting_profile={"intensity": 0.75, "color_temperature": 5500},
            )
            for i in range(3)
        ]
        
        result = self.validator.validate_shot_sequence(frames)
        
        self.assertIn("violations", result)
        self.assertIn("rule_scores", result)
        self.assertIn("overall_consistency", result)
        self.assertEqual(result["total_checks"], 2)

    def test_validate_character_consistency(self):
        """Test validating character consistency"""
        character = CharacterReference(
            character_id="hero_001",
            name="Hero",
            description="Main character",
            appearance_embedding=np.random.rand(64).astype(np.float32),
        )
        
        self.library.add_character(character)
        
        frames = [
            ReferenceFrame(
                frame_id=f"frame_{i}",
                shot_id="shot_001",
                timestamp=i * 0.5,
                embeddings={"character": np.random.rand(64).astype(np.float32)},
                character_ids={"hero_001"},
            )
            for i in range(2)
        ]
        
        result = self.validator.validate_character_consistency("hero_001", frames)
        
        self.assertIn("character_id", result)
        self.assertIn("mean_similarity", result)
        self.assertIn("violations", result)


class TestConsistencyEngine(unittest.TestCase):
    """Test ConsistencyEngine class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = ConsistencyEngine(
            reference_library=ReferenceLibrary(storage_path=self.temp_dir)
        )

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    def test_integrate_scene_analysis(self):
        """Test integrating scene analysis"""
        scene_analysis = {
            "scene_type": {
                "type": "landscape",
                "color_ratios": {"sky": 0.4, "vegetation": 0.3},
            },
            "image_info": {"mean_brightness": 150},
        }
        
        frame = self.engine.integrate_scene_analysis(
            frame_id="test_frame",
            scene_analysis=scene_analysis,
            shot_id="shot_001",
            timestamp=0.5,
        )
        
        self.assertEqual(frame.frame_id, "test_frame")
        self.assertEqual(frame.shot_id, "shot_001")
        self.assertIn("style", frame.embeddings)
        self.assertIsNotNone(frame.lighting_profile)

    def test_check_lighting_consistency(self):
        """Test checking lighting consistency"""
        frame_a = ReferenceFrame(
            frame_id="frame_a",
            shot_id="shot_001",
            timestamp=0.0,
            lighting_profile={"intensity": 0.75, "color_temperature": 5500},
        )
        
        frame_b = ReferenceFrame(
            frame_id="frame_b",
            shot_id="shot_001",
            timestamp=0.5,
            lighting_profile={"intensity": 0.96, "color_temperature": 6501},
        )
        
        violation = self.engine.check_lighting_consistency(frame_a, frame_b)
        
        self.assertIsNotNone(violation)
        self.assertEqual(violation.violation_type, ConsistencyType.LIGHTING)

    def test_check_color_consistency(self):
        """Test checking color consistency"""
        frame_a = ReferenceFrame(
            frame_id="frame_a",
            shot_id="shot_001",
            timestamp=0.0,
            color_histogram=np.array([0.3, 0.2, 0.15, 0.1]),
        )
        
        frame_b = ReferenceFrame(
            frame_id="frame_b",
            shot_id="shot_001",
            timestamp=0.5,
            color_histogram=np.array([0.3, 0.2, 0.15, 0.1]),
        )
        
        violation = self.engine.check_color_consistency(frame_a, frame_b)
        
        self.assertIsNone(violation)

    def test_validate_shot_sequence(self):
        """Test validating shot sequence"""
        frames = [
            ReferenceFrame(
                frame_id=f"frame_{i}",
                shot_id="shot_001",
                timestamp=i * 0.5,
                color_histogram=np.array([0.3, 0.2, 0.15, 0.1]),
                lighting_profile={"intensity": 0.75, "color_temperature": 5500},
            )
            for i in range(3)
        ]
        
        violations = self.engine.validate_shot_sequence(frames)
        
        self.assertIsInstance(violations, list)

    def test_get_consistency_score(self):
        """Test getting consistency score"""
        frames = [
            ReferenceFrame(
                frame_id=f"frame_{i}",
                shot_id="shot_001",
                timestamp=i * 0.5,
                color_histogram=np.array([0.3, 0.2, 0.15, 0.1]),
                lighting_profile={"intensity": 0.75, "color_temperature": 5500},
            )
            for i in range(3)
        ]
        
        scores = self.engine.get_consistency_score(frames)
        
        self.assertIn("overall", scores)
        self.assertIn("character_identity", scores)
        self.assertIn("lighting", scores)
        self.assertIn("color_grading", scores)

    def test_generate_consistency_report(self):
        """Test generating consistency report"""
        frames = [
            ReferenceFrame(
                frame_id=f"frame_{i}",
                shot_id="shot_001",
                timestamp=i * 0.5,
                color_histogram=np.array([0.3, 0.2, 0.15, 0.1]) + np.random.rand(4) * 0.1,
                lighting_profile={
                    "intensity": 0.75 + (i * 0.05),
                    "color_temperature": 5500,
                },
            )
            for i in range(4)
        ]
        
        report = self.engine.generate_consistency_report(frames)
        
        self.assertIn("summary", report)
        self.assertIn("scores_by_type", report)
        self.assertIn("violations", report)
        self.assertIn("recommendations", report)
        
        self.assertEqual(report["summary"]["total_frames"], 4)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestStyleAnchor))
    suite.addTests(loader.loadTestsFromTestCase(TestCharacterReference))
    suite.addTests(loader.loadTestsFromTestCase(TestWorldReference))
    suite.addTests(loader.loadTestsFromTestCase(TestReferenceFrame))
    suite.addTests(loader.loadTestsFromTestCase(TestContinuityRules))
    suite.addTests(loader.loadTestsFromTestCase(TestReferenceLibrary))
    suite.addTests(loader.loadTestsFromTestCase(TestStyleExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossShotValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestConsistencyEngine))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

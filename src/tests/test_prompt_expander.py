"""
Test suite for Prompt Expander and Prompt Compiler
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.prompt_expander import (
    PromptExpander,
    ExpansionRequest,
    DirectorIntent,
    Scene,
    Shot,
    CameraMotion,
    CameraMotionType,
    MotionStrength,
    CharacterConsistency,
    ReferenceFrame,
    ControlMap,
    Storyboard,
    ShotTransition,
    TransitionType,
    DeterminismConfig,
    PromptVersion,
    SchemaVersion,
    ControlVocabulary,
    SeedManager,
    PromptCompiler
)


class TestSeedManager:
    """Test seed management for reproducibility"""
    
    def test_seed_generation(self):
        """Test deterministic seed generation"""
        manager = SeedManager(base_seed=42)
        seed1 = manager.generate_seed("test_context")
        seed2 = manager.generate_seed("test_context")
        
        assert seed1 == seed2, "Same context should produce same seed"
    
    def test_seed_uniqueness(self):
        """Test different contexts produce different seeds"""
        manager = SeedManager(base_seed=42)
        seed1 = manager.generate_seed("context_1")
        seed2 = manager.generate_seed("context_2")
        
        assert seed1 != seed2, "Different contexts should produce different seeds"
    
    def test_manifest_export_import(self):
        """Test seed manifest export and import"""
        manager1 = SeedManager(base_seed=42)
        seed1 = manager1.generate_seed("scene_001:shot_001")
        seed2 = manager1.generate_seed("scene_001:shot_002")
        
        manifest = manager1.export_manifest()
        
        manager2 = SeedManager()
        manager2.import_manifest(manifest)
        
        reproduced1 = manager2.get_or_create_seed("scene_001:shot_001")
        reproduced2 = manager2.get_or_create_seed("scene_001:shot_002")
        
        assert seed1 == reproduced1
        assert seed2 == reproduced2
    
    def test_fixed_seed(self):
        """Test using fixed seed"""
        manager = SeedManager()
        fixed_seed = 12345
        result = manager.get_or_create_seed("test", fixed_seed=fixed_seed)
        
        assert result == fixed_seed


class TestControlVocabulary:
    """Test control vocabulary validation"""
    
    def test_get_vocabulary(self):
        """Test getting complete vocabulary"""
        vocab = ControlVocabulary.get_vocabulary()
        
        assert 'camera_motion' in vocab
        assert 'motion_strength' in vocab
        assert 'control_maps' in vocab
        assert 'fps' in vocab
        assert 'shot_transitions' in vocab
    
    def test_camera_motion_types(self):
        """Test camera motion vocabulary"""
        vocab = ControlVocabulary.get_vocabulary()
        camera_motions = vocab['camera_motion']['types']
        
        assert 'static' in camera_motions
        assert 'dolly_in' in camera_motions
        assert 'pan_left' in camera_motions
        assert 'zoom_in' in camera_motions
    
    def test_motion_strength_levels(self):
        """Test motion strength levels"""
        vocab = ControlVocabulary.get_vocabulary()
        strengths = vocab['motion_strength']
        
        assert 'none' in strengths
        assert 'subtle' in strengths
        assert 'moderate' in strengths
        assert 'strong' in strengths
        assert 'extreme' in strengths
    
    def test_fps_values(self):
        """Test supported FPS values"""
        vocab = ControlVocabulary.get_vocabulary()
        fps_values = vocab['fps']
        
        assert 24 in fps_values
        assert 30 in fps_values
        assert 60 in fps_values


class TestCameraMotion:
    """Test camera motion specifications"""
    
    def test_camera_motion_creation(self):
        """Test creating camera motion"""
        motion = CameraMotion(
            motion_type=CameraMotionType.DOLLY_IN,
            strength=MotionStrength.MODERATE,
            speed=1.0,
            easing="ease_in_out"
        )
        
        assert motion.motion_type == CameraMotionType.DOLLY_IN
        assert motion.strength == MotionStrength.MODERATE
        assert motion.speed == 1.0
        assert motion.easing == "ease_in_out"
    
    def test_motion_types(self):
        """Test various motion types"""
        motions = [
            CameraMotionType.STATIC,
            CameraMotionType.PAN_LEFT,
            CameraMotionType.TILT_UP,
            CameraMotionType.DOLLY_IN,
            CameraMotionType.ZOOM_IN
        ]
        
        for motion_type in motions:
            motion = CameraMotion(motion_type=motion_type)
            assert motion.motion_type == motion_type


class TestCharacterConsistency:
    """Test character consistency controls"""
    
    def test_character_creation(self):
        """Test creating character consistency"""
        character = CharacterConsistency(
            character_id="hero_001",
            reference_frames=[0, 10, 20],
            feature_weights={"face": 1.0, "body": 0.8},
            appearance_locked=True
        )
        
        assert character.character_id == "hero_001"
        assert len(character.reference_frames) == 3
        assert character.appearance_locked is True
    
    def test_feature_weights(self):
        """Test feature weighting"""
        character = CharacterConsistency(
            character_id="char_001",
            feature_weights={
                "face": 1.0,
                "body": 0.9,
                "clothing": 0.8,
                "hair": 0.7
            }
        )
        
        assert character.feature_weights["face"] == 1.0
        assert character.feature_weights["hair"] == 0.7


class TestShot:
    """Test shot specifications"""
    
    def test_shot_creation(self):
        """Test creating a shot"""
        shot = Shot(
            shot_id="shot_001",
            scene_id="scene_001",
            prompt="A wide establishing shot of a city",
            fps=24,
            duration=5.0
        )
        
        assert shot.shot_id == "shot_001"
        assert shot.scene_id == "scene_001"
        assert shot.fps == 24
        assert shot.duration == 5.0
    
    def test_shot_with_camera_motion(self):
        """Test shot with camera motion"""
        motion = CameraMotion(
            motion_type=CameraMotionType.PAN_RIGHT,
            strength=MotionStrength.MODERATE
        )
        
        shot = Shot(
            shot_id="shot_002",
            scene_id="scene_001",
            prompt="Pan across cityscape",
            camera_motion=motion,
            fps=24,
            duration=8.0
        )
        
        assert shot.camera_motion is not None
        assert shot.camera_motion.motion_type == CameraMotionType.PAN_RIGHT
    
    def test_shot_with_determinism(self):
        """Test shot with determinism config"""
        determinism = DeterminismConfig(
            use_fixed_seed=True,
            seed=42
        )
        
        shot = Shot(
            shot_id="shot_003",
            scene_id="scene_001",
            prompt="Close-up shot",
            determinism=determinism,
            fps=24,
            duration=3.0
        )
        
        assert shot.determinism is not None
        assert shot.determinism.seed == 42


class TestScene:
    """Test scene specifications"""
    
    def test_scene_creation(self):
        """Test creating a scene"""
        shot1 = Shot(
            shot_id="shot_001",
            scene_id="scene_001",
            prompt="Establishing shot",
            fps=24,
            duration=5.0
        )
        
        shot2 = Shot(
            shot_id="shot_002",
            scene_id="scene_001",
            prompt="Close-up",
            fps=24,
            duration=3.0
        )
        
        scene = Scene(
            scene_id="scene_001",
            description="Opening scene",
            shots=[shot1, shot2],
            scene_fps=24
        )
        
        assert scene.scene_id == "scene_001"
        assert len(scene.shots) == 2
    
    def test_scene_with_transitions(self):
        """Test scene with shot transitions"""
        transition = ShotTransition(
            from_shot="shot_001",
            to_shot="shot_002",
            transition_type=TransitionType.DISSOLVE,
            duration=1.0
        )
        
        scene = Scene(
            scene_id="scene_001",
            description="Test scene",
            shots=[],
            transitions=[transition],
            scene_fps=24
        )
        
        assert len(scene.transitions) == 1
        assert scene.transitions[0].transition_type == TransitionType.DISSOLVE


class TestDirectorIntent:
    """Test director intent specifications"""
    
    def test_director_intent_creation(self):
        """Test creating director intent"""
        shot = Shot(
            shot_id="shot_001",
            scene_id="scene_001",
            prompt="Test shot",
            fps=24,
            duration=5.0
        )
        
        scene = Scene(
            scene_id="scene_001",
            description="Test scene",
            shots=[shot],
            scene_fps=24
        )
        
        intent = DirectorIntent(
            intent_id="test_intent",
            narrative_description="Test narrative",
            target_providers=["runway", "pika"],
            scenes=[scene]
        )
        
        assert intent.intent_id == "test_intent"
        assert len(intent.scenes) == 1
        assert len(intent.target_providers) == 2
    
    def test_director_intent_versioning(self):
        """Test intent versioning"""
        intent = DirectorIntent(
            intent_id="versioned_intent",
            narrative_description="Test",
            prompt_version=PromptVersion.V2_0,
            schema_version=SchemaVersion.V3_0,
            target_providers=[]
        )
        
        assert intent.prompt_version == PromptVersion.V2_0
        assert intent.schema_version == SchemaVersion.V3_0


class TestPromptCompiler:
    """Test prompt compilation"""
    
    def test_compiler_initialization(self):
        """Test compiler initialization"""
        compiler = PromptCompiler()
        
        assert compiler.seed_manager is not None
        assert compiler.control_vocabulary is not None
        assert len(compiler.provider_adapters) > 0
    
    def test_compile_simple_intent(self):
        """Test compiling simple intent"""
        compiler = PromptCompiler()
        
        shot = Shot(
            shot_id="shot_001",
            scene_id="scene_001",
            prompt="A spaceship flying through space",
            fps=24,
            duration=5.0
        )
        
        scene = Scene(
            scene_id="scene_001",
            description="Space scene",
            shots=[shot],
            scene_fps=24
        )
        
        intent = DirectorIntent(
            intent_id="test_compile",
            narrative_description="Space adventure",
            target_providers=["runway"],
            scenes=[scene]
        )
        
        result = compiler.compile(intent)
        
        assert result.intent_id == "test_compile"
        assert len(result.model_prompts) > 0
        assert len(result.shot_list) == 1
    
    def test_compile_with_determinism(self):
        """Test compilation with determinism"""
        compiler = PromptCompiler()
        
        determinism = DeterminismConfig(
            use_fixed_seed=True,
            seed=42
        )
        
        shot = Shot(
            shot_id="shot_001",
            scene_id="scene_001",
            prompt="Test shot",
            fps=24,
            duration=5.0,
            determinism=determinism
        )
        
        scene = Scene(
            scene_id="scene_001",
            description="Test",
            shots=[shot],
            scene_fps=24
        )
        
        intent = DirectorIntent(
            intent_id="deterministic_intent",
            narrative_description="Test",
            target_providers=["runway"],
            scenes=[scene],
            global_determinism=determinism
        )
        
        result = compiler.compile(intent)
        
        assert len(result.seed_manifest) > 0
        assert result.compilation_metadata['num_shots'] == 1
    
    def test_compile_multiple_providers(self):
        """Test compilation for multiple providers"""
        compiler = PromptCompiler()
        
        shot = Shot(
            shot_id="shot_001",
            scene_id="scene_001",
            prompt="Multi-provider test",
            fps=24,
            duration=5.0
        )
        
        scene = Scene(
            scene_id="scene_001",
            description="Test",
            shots=[shot],
            scene_fps=24
        )
        
        intent = DirectorIntent(
            intent_id="multi_provider",
            narrative_description="Test",
            target_providers=["runway", "pika", "sora"],
            scenes=[scene]
        )
        
        result = compiler.compile(intent)
        
        providers = [p.provider for p in result.model_prompts]
        assert "runway" in providers
        assert "pika" in providers
        assert "sora" in providers
    
    def test_motion_strength_mapping(self):
        """Test motion strength mapping"""
        compiler = PromptCompiler()
        
        runway_value = compiler._map_motion_strength(MotionStrength.MODERATE)
        assert runway_value == 5
        
        extreme_value = compiler._map_motion_strength(MotionStrength.EXTREME)
        assert extreme_value == 10
        
        pika_value = compiler._map_motion_strength_pika(MotionStrength.MODERATE)
        assert pika_value == 0.5


class TestStoryboard:
    """Test storyboard specifications"""
    
    def test_storyboard_creation(self):
        """Test creating a storyboard panel"""
        storyboard = Storyboard(
            panel_id="panel_001",
            shot_number="1A",
            description="Hero stands on cliff",
            camera_angle="low angle",
            composition="rule of thirds",
            duration=3.0
        )
        
        assert storyboard.panel_id == "panel_001"
        assert storyboard.shot_number == "1A"
        assert storyboard.duration == 3.0


class TestControlMap:
    """Test control map specifications"""
    
    def test_control_map_creation(self):
        """Test creating control maps"""
        depth_map = ControlMap(
            map_type="depth",
            map_data="/path/to/depth.png",
            strength=0.8,
            preprocessor="depth_midas"
        )
        
        assert depth_map.map_type == "depth"
        assert depth_map.strength == 0.8
        assert depth_map.preprocessor == "depth_midas"
    
    def test_control_map_temporal_range(self):
        """Test control map temporal range"""
        pose_map = ControlMap(
            map_type="pose",
            map_data="/path/to/pose.json",
            strength=1.0,
            start_frame=0,
            end_frame=120
        )
        
        assert pose_map.start_frame == 0
        assert pose_map.end_frame == 120


class TestReferenceFrame:
    """Test reference frame specifications"""
    
    def test_reference_frame_creation(self):
        """Test creating reference frames"""
        ref = ReferenceFrame(
            frame_id="ref_001",
            timestamp=0.0,
            image_path="/path/to/image.jpg",
            weight=1.0,
            aspect="full"
        )
        
        assert ref.frame_id == "ref_001"
        assert ref.weight == 1.0
        assert ref.aspect == "full"


class TestTransitions:
    """Test shot transitions"""
    
    def test_transition_types(self):
        """Test various transition types"""
        transitions = [
            TransitionType.CUT,
            TransitionType.FADE,
            TransitionType.DISSOLVE,
            TransitionType.WIPE
        ]
        
        for trans_type in transitions:
            transition = ShotTransition(
                from_shot="shot_001",
                to_shot="shot_002",
                transition_type=trans_type,
                duration=1.0
            )
            assert transition.transition_type == trans_type


class TestIntegration:
    """Integration tests for full workflow"""
    
    def test_full_compilation_workflow(self):
        """Test complete compilation workflow"""
        expander = PromptExpander()
        
        camera_motion = CameraMotion(
            motion_type=CameraMotionType.DOLLY_IN,
            strength=MotionStrength.MODERATE,
            speed=1.0
        )
        
        character = CharacterConsistency(
            character_id="hero",
            reference_frames=[0, 10],
            feature_weights={"face": 1.0},
            appearance_locked=True
        )
        
        shot1 = Shot(
            shot_id="shot_001",
            scene_id="scene_001",
            prompt="Opening shot of city",
            camera_motion=camera_motion,
            characters=[character],
            fps=24,
            duration=5.0
        )
        
        shot2 = Shot(
            shot_id="shot_002",
            scene_id="scene_001",
            prompt="Close-up of character",
            characters=[character],
            fps=24,
            duration=3.0
        )
        
        transition = ShotTransition(
            from_shot="shot_001",
            to_shot="shot_002",
            transition_type=TransitionType.CUT,
            duration=0.0
        )
        
        scene = Scene(
            scene_id="scene_001",
            description="Opening scene",
            shots=[shot1, shot2],
            transitions=[transition],
            scene_fps=24
        )
        
        intent = DirectorIntent(
            intent_id="integration_test",
            narrative_description="Test narrative",
            style_references=["Test Style"],
            mood="dramatic",
            visual_theme="cinematic",
            target_providers=["runway", "pika"],
            scenes=[scene],
            global_determinism=DeterminismConfig(seed=42, use_fixed_seed=True)
        )
        
        result = expander.compile_director_intent(intent)
        
        assert result.intent_id == "integration_test"
        assert len(result.model_prompts) >= 2
        assert len(result.shot_list) == 2
        assert len(result.scene_breakdown) == 1
        assert len(result.seed_manifest) > 0
        assert result.compilation_time > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Unit tests for Director UX Control Surface
"""

import pytest
import json
from datetime import datetime
from src.core.director_ux import (
    DirectorControls,
    DirectorMode,
    CameraControl,
    CameraMovementType,
    CameraAngle,
    ShotType,
    TimingControl,
    MotionControl,
    MotionStrengthLevel,
    TransitionControl,
    TransitionStyle,
    StylePreset,
    PresetLibrary,
    IterationWorkflow,
    AutoModeAssistant,
    GenerationComparison,
    ParameterLock
)


class TestCameraControl:
    """Tests for CameraControl"""
    
    def test_camera_control_defaults(self):
        camera = CameraControl()
        assert camera.movement_type == CameraMovementType.STATIC
        assert camera.angle == CameraAngle.EYE_LEVEL
        assert camera.shot_type == ShotType.MEDIUM
        assert camera.focal_length == 50
        assert camera.speed == 1.0
    
    def test_camera_control_custom(self):
        camera = CameraControl(
            movement_type=CameraMovementType.DOLLY,
            shot_type=ShotType.CLOSEUP,
            focal_length=85,
            speed=0.8
        )
        assert camera.movement_type == CameraMovementType.DOLLY
        assert camera.shot_type == ShotType.CLOSEUP
        assert camera.focal_length == 85
        assert camera.speed == 0.8
    
    def test_camera_to_internal_params(self):
        camera = CameraControl(
            movement_type=CameraMovementType.DOLLY,
            speed=0.8,
            strength=MotionStrengthLevel.MODERATE
        )
        params = camera.to_internal_params()
        
        assert 'camera_motion' in params
        assert params['camera_motion']['type'] == 'dolly'
        assert params['camera_motion']['speed'] == 0.8
        assert params['camera_motion']['strength'] == 'moderate'
        assert params['camera_angle'] == 'eye_level'
        assert params['shot_type'] == 'medium'


class TestTimingControl:
    """Tests for TimingControl"""
    
    def test_timing_defaults(self):
        timing = TimingControl()
        assert timing.duration == 5.0
        assert timing.fps == 24
        assert timing.speed_factor == 1.0
    
    def test_timing_custom(self):
        timing = TimingControl(duration=7.5, fps=30, speed_factor=0.5)
        assert timing.duration == 7.5
        assert timing.fps == 30
        assert timing.speed_factor == 0.5
    
    def test_timing_to_internal_params(self):
        timing = TimingControl(duration=7.0, fps=30)
        params = timing.to_internal_params()
        
        assert params['duration'] == 7.0
        assert params['fps'] == 30
        assert params['speed_factor'] == 1.0


class TestMotionControl:
    """Tests for MotionControl"""
    
    def test_motion_defaults(self):
        motion = MotionControl()
        assert motion.overall_strength == MotionStrengthLevel.MODERATE
        assert motion.subject_motion == 0.5
        assert motion.motion_blur is True
    
    def test_motion_custom(self):
        motion = MotionControl(
            overall_strength=MotionStrengthLevel.STRONG,
            subject_motion=0.8,
            motion_blur=False
        )
        assert motion.overall_strength == MotionStrengthLevel.STRONG
        assert motion.subject_motion == 0.8
        assert motion.motion_blur is False
    
    def test_motion_to_internal_params(self):
        motion = MotionControl(overall_strength=MotionStrengthLevel.STRONG)
        params = motion.to_internal_params()
        
        assert params['motion_strength'] == 'strong'
        assert params['subject_motion'] == 0.5
        assert params['motion_blur'] is True


class TestTransitionControl:
    """Tests for TransitionControl"""
    
    def test_transition_defaults(self):
        transition = TransitionControl()
        assert transition.style == TransitionStyle.CUT
        assert transition.duration == 1.0
    
    def test_transition_custom(self):
        transition = TransitionControl(
            style=TransitionStyle.DISSOLVE,
            duration=1.5,
            offset=0.2
        )
        assert transition.style == TransitionStyle.DISSOLVE
        assert transition.duration == 1.5
        assert transition.offset == 0.2
    
    def test_transition_to_internal_params(self):
        transition = TransitionControl(
            style=TransitionStyle.FADE,
            duration=2.0
        )
        params = transition.to_internal_params()
        
        assert params['transition_type'] == 'fade'
        assert params['duration'] == 2.0


class TestDirectorControls:
    """Tests for DirectorControls"""
    
    def test_director_controls_defaults(self):
        controls = DirectorControls()
        assert controls.mode == DirectorMode.AUTO
        assert isinstance(controls.camera, CameraControl)
        assert isinstance(controls.timing, TimingControl)
        assert isinstance(controls.motion, MotionControl)
        assert controls.control_id is not None
    
    def test_director_controls_pro_mode(self):
        controls = DirectorControls(mode=DirectorMode.PRO)
        assert controls.mode == DirectorMode.PRO
    
    def test_to_internal_params(self):
        controls = DirectorControls(mode=DirectorMode.PRO)
        controls.camera.movement_type = CameraMovementType.DOLLY
        controls.timing.duration = 7.0
        
        params = controls.to_internal_params()
        
        assert 'camera_motion' in params
        assert params['duration'] == 7.0
        assert params['fps'] == 24
        assert 'motion_strength' in params
    
    def test_parameter_locking(self):
        controls = DirectorControls()
        
        controls.lock_parameter("camera.speed", 0.8, "Perfect speed")
        
        assert "camera.speed" in controls.locked_parameters
        assert controls.locked_parameters["camera.speed"].locked is True
        assert controls.locked_parameters["camera.speed"].locked_value == 0.8
        assert controls.locked_parameters["camera.speed"].notes == "Perfect speed"
    
    def test_parameter_unlocking(self):
        controls = DirectorControls()
        controls.lock_parameter("camera.speed", 0.8)
        
        controls.unlock_parameter("camera.speed")
        
        assert controls.locked_parameters["camera.speed"].locked is False
    
    def test_add_comparison(self):
        controls = DirectorControls()
        
        comp = GenerationComparison(
            generation_id="gen_001",
            parameters={"speed": 0.8},
            rating=4,
            notes="Good result"
        )
        controls.add_comparison(comp)
        
        assert len(controls.generation_history) == 1
        assert controls.generation_history[0].generation_id == "gen_001"
    
    def test_get_best_generation(self):
        controls = DirectorControls()
        
        comparisons = [
            GenerationComparison("gen_001", {}, rating=3, notes="OK"),
            GenerationComparison("gen_002", {}, rating=5, notes="Best"),
            GenerationComparison("gen_003", {}, rating=4, notes="Good")
        ]
        
        for comp in comparisons:
            controls.add_comparison(comp)
        
        best = controls.get_best_generation()
        assert best.generation_id == "gen_002"
        assert best.rating == 5
    
    def test_to_dict_from_dict(self):
        controls = DirectorControls(mode=DirectorMode.PRO)
        controls.camera.movement_type = CameraMovementType.DOLLY
        controls.timing.duration = 7.0
        
        data = controls.to_dict()
        restored = DirectorControls.from_dict(data)
        
        assert restored.mode == DirectorMode.PRO
        assert restored.camera.movement_type == CameraMovementType.DOLLY
        assert restored.timing.duration == 7.0


class TestPresetLibrary:
    """Tests for PresetLibrary"""
    
    def test_list_presets(self):
        presets = PresetLibrary.list_presets()
        assert len(presets) == 6
        assert all('name' in p for p in presets)
        assert all('description' in p for p in presets)
        assert all('use_case' in p for p in presets)
    
    def test_get_documentary_preset(self):
        controls = PresetLibrary.get_preset(StylePreset.DOCUMENTARY)
        assert controls.style_preset == StylePreset.DOCUMENTARY
        assert controls.camera.movement_type == CameraMovementType.HANDHELD
        assert controls.motion.overall_strength == MotionStrengthLevel.SUBTLE
        assert controls.visual_style == "naturalistic"
    
    def test_get_commercial_preset(self):
        controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
        assert controls.style_preset == StylePreset.COMMERCIAL
        assert controls.camera.movement_type == CameraMovementType.DOLLY
        assert controls.timing.fps == 30
        assert controls.visual_style == "polished"
    
    def test_get_art_house_preset(self):
        controls = PresetLibrary.get_preset(StylePreset.ART_HOUSE)
        assert controls.style_preset == StylePreset.ART_HOUSE
        assert controls.camera.movement_type == CameraMovementType.TRACKING_SHOT
        assert controls.timing.duration == 12.0
        assert controls.color_grade == "desaturated"
    
    def test_get_action_preset(self):
        controls = PresetLibrary.get_preset(StylePreset.ACTION)
        assert controls.style_preset == StylePreset.ACTION
        assert controls.motion.overall_strength == MotionStrengthLevel.EXTREME
        assert controls.timing.fps == 60
        assert controls.mood == "intense"
    
    def test_get_drama_preset(self):
        controls = PresetLibrary.get_preset(StylePreset.DRAMA)
        assert controls.style_preset == StylePreset.DRAMA
        assert controls.camera.shot_type == ShotType.CLOSEUP
        assert controls.camera.focal_length == 85
        assert controls.depth_of_field == 0.2
    
    def test_get_music_video_preset(self):
        controls = PresetLibrary.get_preset(StylePreset.MUSIC_VIDEO)
        assert controls.style_preset == StylePreset.MUSIC_VIDEO
        assert controls.camera.movement_type == CameraMovementType.ORBIT
        assert controls.color_grade == "saturated"


class TestIterationWorkflow:
    """Tests for IterationWorkflow"""
    
    def test_create_variation(self):
        controls = DirectorControls()
        controls.camera.speed = 1.0
        
        workflow = IterationWorkflow(controls)
        variation = workflow.create_variation({"camera.speed": 1.5})
        
        assert variation.camera.speed == 1.5
        assert variation.control_id != controls.control_id
    
    def test_create_variation_respects_locks(self):
        controls = DirectorControls()
        controls.camera.speed = 1.0
        controls.lock_parameter("camera.speed", 1.0, "Locked")
        
        workflow = IterationWorkflow(controls)
        variation = workflow.create_variation(
            {"camera.speed": 2.0},
            preserve_locked=True
        )
        
        # Locked parameter should not change
        assert variation.camera.speed == 1.0
    
    def test_compare_generations(self):
        controls = DirectorControls()
        workflow = IterationWorkflow(controls)
        
        generations = [
            GenerationComparison("gen_001", {}, rating=3, notes="OK"),
            GenerationComparison("gen_002", {}, rating=5, notes="Best"),
            GenerationComparison("gen_003", {}, rating=4, notes="Good")
        ]
        
        comparison = workflow.compare_generations(generations)
        
        assert comparison['total_generations'] == 3
        assert comparison['rated_count'] == 3
        assert comparison['best_generation'] == "gen_002"
        assert comparison['average_rating'] == 4.0
    
    def test_suggest_refinements_speed(self):
        controls = DirectorControls()
        controls.camera.speed = 1.8
        
        workflow = IterationWorkflow(controls)
        suggestions = workflow.suggest_refinements(
            controls,
            "Camera moves too fast and feels rushed"
        )
        
        assert len(suggestions) > 0
        assert any('speed' in s['parameter'] for s in suggestions)
    
    def test_suggest_refinements_duration(self):
        controls = DirectorControls()
        controls.timing.duration = 3.0
        
        workflow = IterationWorkflow(controls)
        suggestions = workflow.suggest_refinements(
            controls,
            "Too short, can't see what's happening"
        )
        
        assert len(suggestions) > 0
        assert any('duration' in s['parameter'] for s in suggestions)


class TestAutoModeAssistant:
    """Tests for AutoModeAssistant"""
    
    def test_get_quick_options(self):
        options = AutoModeAssistant.get_quick_options()
        
        assert 'content_types' in options
        assert 'moods' in options
        assert 'durations' in options
        assert len(options['content_types']) > 0
        assert len(options['moods']) > 0
    
    def test_suggest_controls_product(self):
        controls = AutoModeAssistant.suggest_controls(
            content_type="product",
            mood="exciting",
            duration=5.0
        )
        
        assert controls.mode == DirectorMode.AUTO
        assert controls.timing.duration == 5.0
        assert controls.mood == "exciting"
        assert controls.style_preset is not None
    
    def test_suggest_controls_calm_mood(self):
        controls = AutoModeAssistant.suggest_controls(
            content_type="interview",
            mood="calm",
            duration=8.0
        )
        
        assert controls.camera.speed <= 1.0
        assert controls.motion.overall_strength in [
            MotionStrengthLevel.SUBTLE,
            MotionStrengthLevel.MODERATE
        ]
    
    def test_suggest_controls_exciting_mood(self):
        controls = AutoModeAssistant.suggest_controls(
            content_type="sport",
            mood="exciting",
            duration=5.0
        )
        
        assert controls.camera.speed >= 1.0
        assert controls.motion.overall_strength in [
            MotionStrengthLevel.MODERATE,
            MotionStrengthLevel.STRONG,
            MotionStrengthLevel.EXTREME
        ]


class TestGenerationComparison:
    """Tests for GenerationComparison"""
    
    def test_generation_comparison_creation(self):
        comp = GenerationComparison(
            generation_id="gen_001",
            parameters={"speed": 0.8},
            rating=4,
            notes="Good result"
        )
        
        assert comp.generation_id == "gen_001"
        assert comp.parameters == {"speed": 0.8}
        assert comp.rating == 4
        assert comp.notes == "Good result"
        assert comp.created_at is not None


class TestIntegration:
    """Integration tests"""
    
    def test_full_pro_workflow(self):
        # Start with preset
        controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
        
        # Customize
        controls.timing.duration = 7.0
        controls.camera.speed = 0.8
        
        # Lock parameters
        controls.lock_parameter("camera.movement_type", "dolly")
        controls.lock_parameter("timing.fps", 30)
        
        # Create variation
        workflow = IterationWorkflow(controls)
        variation = workflow.create_variation({"camera.speed": 1.0})
        
        # Verify
        assert variation.camera.speed == 1.0
        assert variation.timing.fps == 30  # Locked value preserved
        
        # Convert to params
        params = variation.to_internal_params()
        assert 'duration' in params
        assert 'fps' in params
        assert 'camera_motion' in params
    
    def test_auto_to_pro_upgrade(self):
        # Start in auto mode
        controls = AutoModeAssistant.suggest_controls(
            content_type="product",
            mood="calm",
            duration=5.0
        )
        
        assert controls.mode == DirectorMode.AUTO
        
        # Switch to pro mode
        controls.mode = DirectorMode.PRO
        controls.camera.focal_length = 85
        controls.depth_of_field = 0.3
        
        assert controls.mode == DirectorMode.PRO
        assert controls.camera.focal_length == 85
        
        # Generate params
        params = controls.to_internal_params()
        assert params['focal_length'] == 85
        assert params['depth_of_field'] == 0.3
    
    def test_serialization_roundtrip(self):
        # Create controls
        controls = PresetLibrary.get_preset(StylePreset.DRAMA)
        controls.timing.duration = 6.5
        controls.lock_parameter("camera.speed", 0.5)
        
        # Serialize
        data = controls.to_dict()
        json_str = json.dumps(data)
        
        # Deserialize
        restored_data = json.loads(json_str)
        restored = DirectorControls.from_dict(restored_data)
        
        # Verify
        assert restored.style_preset == StylePreset.DRAMA
        assert restored.timing.duration == 6.5
        assert "camera.speed" in restored.locked_parameters


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

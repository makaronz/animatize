"""
Comprehensive test suite for wedge features
Tests all 8 strategic wedge features
"""

import pytest
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from wedge_features.film_grammar import FilmGrammarEngine, Genre, CulturalContext, GrammarRule
from wedge_features.shot_list_compiler import ShotListCompiler, ShotType, CameraMovement
from wedge_features.consistency_engine import ConsistencyEngine, ReferenceManager, ReferenceFrame, ConsistencyType
from wedge_features.evaluation_harness import EvaluationHarness, GoldenDataset, TestScenario
from wedge_features.temporal_control import TemporalControlLayer, KeyframeEditor, EasingFunction
from wedge_features.quality_assurance import QualityAssuranceSystem, QualityScorer, QualityMetric
from wedge_features.identity_preservation import CharacterIdentityEngine, IdentityTracker
from wedge_features.collaborative_workflow import CollaborativeWorkflow, UserRole, ProjectManager


class TestFilmGrammarEngine:
    """Test Film Grammar Engine"""
    
    def test_engine_initialization(self, tmp_path):
        engine = FilmGrammarEngine(grammar_db_path=str(tmp_path / "test_grammar.json"))
        assert len(engine.rules) >= 5
        assert len(engine.genre_rules) > 0
    
    def test_get_applicable_rules(self):
        engine = FilmGrammarEngine()
        rules = engine.get_applicable_rules(genre=Genre.DRAMA, min_priority=0.8)
        assert len(rules) > 0
        assert all(r.priority >= 0.8 for r in rules)
    
    def test_validate_grammar(self):
        engine = FilmGrammarEngine()
        scene = {
            'type': 'dialogue',
            'tags': ['scene_with_dialogue', 'two_or_more_subjects'],
            'elements': []
        }
        validation = engine.validate_grammar(scene, ['FG_001'], strict_mode=False)
        assert validation.is_valid or len(validation.violations) < 3
    
    def test_learn_from_feedback(self):
        engine = FilmGrammarEngine()
        initial_confidence = engine.rules['FG_001'].confidence
        engine.learn_from_feedback('FG_001', {'rating': 0.95})
        assert engine.rules['FG_001'].confidence >= initial_confidence
    
    def test_coverage_stats(self):
        engine = FilmGrammarEngine()
        stats = engine.get_coverage_stats()
        assert 'total_rules' in stats
        assert 'validated_rules' in stats
        assert stats['total_rules'] >= 5


class TestShotListCompiler:
    """Test Shot List Compiler"""
    
    def test_compiler_initialization(self):
        compiler = ShotListCompiler()
        assert len(compiler.coverage_templates) > 0
    
    def test_parse_script(self):
        compiler = ShotListCompiler()
        script = """
        INT. OFFICE - DAY
        
        John enters the room.
        
        EXT. PARK - NIGHT
        
        Sarah sits on a bench.
        """
        scenes = compiler.parse_script(script)
        assert len(scenes) == 2
        assert 'OFFICE' in scenes[0].location
    
    def test_generate_coverage(self):
        compiler = ShotListCompiler()
        from wedge_features.shot_list_compiler import Scene
        
        scene = Scene(
            scene_number="SCENE_001",
            description="INT. OFFICE - DAY",
            location="OFFICE",
            time_of_day="DAY"
        )
        
        shots = compiler.generate_coverage(scene, scene_type='dialogue')
        assert len(shots) > 0
        assert any(s.shot_type == ShotType.WIDE for s in shots)
    
    def test_estimate_resources(self):
        compiler = ShotListCompiler()
        from wedge_features.shot_list_compiler import Scene, Shot
        
        scene = Scene(
            scene_number="SCENE_001",
            description="Test",
            location="OFFICE",
            time_of_day="DAY"
        )
        
        scene.shots.append(Shot(
            shot_number="001",
            scene_number="SCENE_001",
            shot_type=ShotType.WIDE,
            description="Master",
            camera_movement=CameraMovement.DOLLY,
            duration_estimate=30.0,
            angle="eye level"
        ))
        
        resources = compiler.estimate_resources(scene)
        assert 'equipment' in resources
        assert 'dolly_track' in resources['equipment']
    
    def test_completeness_score(self):
        compiler = ShotListCompiler()
        compiler.parse_script("INT. OFFICE - DAY\n\nTest scene.")
        
        if compiler.scenes:
            compiler.generate_coverage(compiler.scenes[0])
            score = compiler.calculate_completeness_score()
            assert 0 <= score <= 100


class TestConsistencyEngine:
    """Test Consistency Engine"""
    
    def test_reference_manager(self):
        manager = ReferenceManager()
        
        frame = ReferenceFrame(
            frame_id="test_001",
            shot_id="shot_001",
            timestamp=0.0
        )
        
        assert manager.add_reference(frame, tags=['character:john'])
        assert manager.get_reference("test_001") is not None
    
    def test_character_consistency(self):
        engine = ConsistencyEngine()
        
        frame_a = ReferenceFrame(
            frame_id="frame_001",
            shot_id="shot_001",
            timestamp=0.0,
            embeddings={'character': np.random.rand(512)}
        )
        
        frame_b = ReferenceFrame(
            frame_id="frame_002",
            shot_id="shot_001",
            timestamp=1.0,
            embeddings={'character': frame_a.embeddings['character'] + np.random.rand(512) * 0.01}
        )
        
        violation = engine.check_character_consistency(frame_a, frame_b, "test_character")
        assert violation is None or violation.confidence > 0.5
    
    def test_consistency_report(self):
        engine = ConsistencyEngine()
        
        frames = [
            ReferenceFrame(
                frame_id=f"frame_{i}",
                shot_id="shot_001",
                timestamp=float(i),
                embeddings={'character': np.random.rand(512)}
            )
            for i in range(5)
        ]
        
        report = engine.generate_consistency_report(frames)
        assert 'summary' in report
        assert 'scores_by_type' in report


class TestEvaluationHarness:
    """Test Evaluation Harness"""
    
    def test_golden_dataset(self):
        dataset = GoldenDataset()
        assert len(dataset.test_cases) >= 2
    
    def test_run_test_case(self):
        harness = EvaluationHarness()
        test_case = list(harness.golden_dataset.test_cases.values())[0]
        
        generated = {
            'metrics': {
                'temporal_coherence': 0.90,
                'motion_smoothness': 0.92,
                'identity_preservation': 0.96
            }
        }
        
        result = harness.run_test_case(test_case, generated)
        assert result.test_id == test_case.test_id
        assert result.passed or len(result.violations) > 0
    
    def test_regression_detection(self):
        harness = EvaluationHarness()
        
        from wedge_features.evaluation_harness import EvaluationResult
        
        result = EvaluationResult(
            test_id="GT_001",
            passed=True,
            quality_scores={'temporal_coherence': 0.90},
            metrics={},
            violations=[],
            execution_time=1.0,
            confidence=0.9
        )
        
        harness.set_baseline([result])
        
        degraded_result = EvaluationResult(
            test_id="GT_001",
            passed=False,
            quality_scores={'temporal_coherence': 0.70},
            metrics={},
            violations=[],
            execution_time=1.0,
            confidence=0.9
        )
        
        regressions = harness.detect_regression([degraded_result])
        assert len(regressions) > 0


class TestTemporalControl:
    """Test Temporal Control Layer"""
    
    def test_keyframe_editor(self):
        editor = KeyframeEditor()
        
        assert editor.add_keyframe(
            'camera_motion',
            0.0,
            {'pos_x': 0.0, 'pos_y': 0.0, 'pos_z': 0.0}
        )
        
        assert editor.add_keyframe(
            'camera_motion',
            5.0,
            {'pos_x': 10.0, 'pos_y': 5.0, 'pos_z': 2.0}
        )
        
        value = editor.interpolate_value('camera_motion', 2.5, 'pos_x')
        assert value is not None
        assert 0.0 <= value <= 10.0
    
    def test_temporal_layer(self):
        layer = TemporalControlLayer(fps=24)
        
        assert layer.add_motion_keyframe(
            0.0,
            camera_position=(0.0, 0.0, 0.0),
            zoom=1.0
        )
        
        frames = layer.generate_frame_sequence(duration=2.0)
        assert len(frames) == 48
    
    def test_speed_ramp(self):
        layer = TemporalControlLayer()
        assert layer.apply_speed_ramp(0.0, 5.0, start_speed=1.0, end_speed=0.5)


class TestQualityAssurance:
    """Test Quality Assurance System"""
    
    def test_quality_scorer(self):
        scorer = QualityScorer()
        
        resolution_score = scorer.score_resolution(1920, 1080)
        assert resolution_score == 1.0
        
        resolution_score_low = scorer.score_resolution(1280, 720)
        assert resolution_score_low < 1.0
    
    def test_qa_system(self):
        qa = QualityAssuranceSystem()
        
        video_data = {
            'width': 1920,
            'height': 1080,
            'fps': 24,
            'codec': 'h264',
            'bitrate': 8000,
            'frames': []
        }
        
        report = qa.assess_quality(video_data)
        assert 0.0 <= report.overall_score <= 1.0
        assert 'resolution' in report.scores_by_metric
    
    def test_generate_report(self):
        qa = QualityAssuranceSystem()
        
        video_data = {
            'width': 1920,
            'height': 1080,
            'fps': 24,
            'codec': 'h264',
            'bitrate': 8000,
            'frames': []
        }
        
        report = qa.assess_quality(video_data)
        report_text = qa.generate_qa_report(report)
        assert len(report_text) > 0
        assert "QUALITY ASSURANCE REPORT" in report_text


class TestCharacterIdentity:
    """Test Character Identity Preservation"""
    
    def test_identity_tracker(self):
        tracker = IdentityTracker()
        
        from wedge_features.identity_preservation import CharacterProfile
        
        profile = CharacterProfile(
            character_id="char_001",
            name="John",
            embeddings=np.random.rand(512),
            reference_images=["ref1.jpg"],
            appearance_features={}
        )
        
        frames = [
            {
                'frame_number': i,
                'face_detections': [
                    {
                        'embedding': profile.embeddings + np.random.rand(512) * 0.01,
                        'bbox': (100, 100, 200, 200)
                    }
                ]
            }
            for i in range(5)
        ]
        
        results = tracker.track_across_frames(frames, [profile])
        assert len(results) == 5
    
    def test_identity_engine(self, tmp_path):
        engine = CharacterIdentityEngine(storage_path=str(tmp_path))
        
        assert engine.add_character(
            "char_001",
            "John Doe",
            ["ref1.jpg", "ref2.jpg"],
            {"hair": "brown", "eyes": "blue"}
        )
        
        assert "char_001" in engine.character_profiles
    
    def test_identity_in_prompt(self):
        engine = CharacterIdentityEngine()
        engine.add_character("char_001", "Jane", ["ref.jpg"])
        
        prompt = engine.preserve_identity_in_generation(
            "char_001",
            "Walking down the street"
        )
        
        assert "Jane" in prompt
        assert "Walking down the street" in prompt


class TestCollaborativeWorkflow:
    """Test Collaborative Workflow"""
    
    def test_project_manager(self, tmp_path):
        manager = ProjectManager(storage_path=str(tmp_path))
        
        project = manager.create_project("proj_001", "Test Project", "user_001")
        assert project.project_id == "proj_001"
        assert "user_001" in project.members
    
    def test_collaborative_workflow(self, tmp_path):
        workflow = CollaborativeWorkflow(storage_path=str(tmp_path))
        
        user = workflow.register_user("user_001", "John Doe", "john@example.com", UserRole.EDITOR)
        assert user.user_id == "user_001"
        assert 'write' in user.permissions
    
    def test_comments(self):
        workflow = CollaborativeWorkflow()
        workflow.register_user("user_001", "John", "john@test.com")
        
        comment = workflow.add_comment(
            "comment_001",
            "user_001",
            "asset_001",
            "Great work!",
            frame_number=42
        )
        
        assert comment.comment_id == "comment_001"
        assert comment.frame_number == 42
    
    def test_version_control(self):
        workflow = CollaborativeWorkflow()
        workflow.register_user("user_001", "John", "john@test.com")
        
        version = workflow.create_version(
            "v001",
            "asset_001",
            "user_001",
            ["Updated prompt", "Improved composition"],
            "/path/to/file.mp4"
        )
        
        assert version.version_number == 1
        assert len(version.changes) == 2
    
    def test_collaboration_stats(self):
        workflow = CollaborativeWorkflow()
        workflow.register_user("user_001", "John", "john@test.com")
        
        workflow.add_comment("c1", "user_001", "asset_001", "test", None)
        workflow.create_version("v1", "asset_001", "user_001", ["test"], "/test")
        
        workflow._log_activity('test', 'user_001', {}, project_id='proj_001')
        
        stats = workflow.get_collaboration_stats('proj_001')
        assert 'total_activities' in stats
        assert stats['total_activities'] >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

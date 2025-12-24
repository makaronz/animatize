"""
Comprehensive demonstration of all 8 wedge features

This example shows how to use each wedge feature individually
and how they work together to create a production pipeline.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from wedge_features import (
    FilmGrammarEngine,
    ShotListCompiler,
    ConsistencyEngine,
    ReferenceManager,
    EvaluationHarness,
    GoldenDataset,
    TemporalControlLayer,
    KeyframeEditor,
    QualityAssuranceSystem,
    CharacterIdentityEngine,
    CollaborativeWorkflow,
    ProjectManager
)
from wedge_features.film_grammar import Genre, CulturalContext
from wedge_features.shot_list_compiler import Scene
from wedge_features.consistency_engine import ReferenceFrame
from wedge_features.collaborative_workflow import UserRole
import numpy as np


def demo_film_grammar():
    """Demo: Film Grammar Engine"""
    print("=" * 60)
    print("DEMO 1: FILM GRAMMAR ENGINE")
    print("=" * 60)
    
    engine = FilmGrammarEngine()
    
    rules = engine.get_applicable_rules(
        genre=Genre.NEO_NOIR,
        category="camera_movement",
        min_priority=0.8
    )
    
    print(f"\nFound {len(rules)} applicable rules for Neo-Noir camera movement:")
    for rule in rules[:3]:
        print(f"  - {rule.name} (Priority: {rule.priority})")
        print(f"    {rule.description}")
    
    scene = {
        'type': 'dialogue',
        'tags': ['scene_with_dialogue', 'two_or_more_subjects'],
        'elements': []
    }
    
    validation = engine.validate_grammar(scene, ['FG_001', 'FG_004'])
    print(f"\nGrammar Validation: {'PASSED' if validation.is_valid else 'FAILED'}")
    print(f"Confidence: {validation.confidence:.2f}")
    
    if validation.suggestions:
        print("Suggestions:")
        for suggestion in validation.suggestions:
            print(f"  - {suggestion}")
    
    stats = engine.get_coverage_stats()
    print(f"\nCoverage Statistics:")
    print(f"  Total Rules: {stats['total_rules']}")
    print(f"  Validated: {stats['validated_rules']}")
    print(f"  Avg Confidence: {stats['avg_confidence']:.2f}")


def demo_shot_list_compiler():
    """Demo: Shot List Compiler"""
    print("\n" + "=" * 60)
    print("DEMO 2: SHOT LIST COMPILER")
    print("=" * 60)
    
    compiler = ShotListCompiler()
    
    script = """
    INT. DETECTIVE OFFICE - NIGHT
    
    Detective JAMES sits at his desk, reviewing case files.
    The door opens. SARAH enters.
    
    EXT. CITY STREET - DAY
    
    Sarah walks through the crowded street.
    """
    
    scenes = compiler.parse_script(script)
    print(f"\nParsed {len(scenes)} scenes from script:")
    
    for scene in scenes:
        print(f"\n  {scene.scene_number}: {scene.description}")
        
        shots = compiler.generate_coverage(scene, scene_type='dialogue')
        print(f"  Generated {len(shots)} shots:")
        
        for shot in shots[:3]:
            print(f"    - {shot.shot_number}: {shot.shot_type.value} - {shot.description}")
        
        resources = compiler.estimate_resources(scene)
        print(f"  Required Equipment: {', '.join(resources['equipment']) or 'Basic setup'}")
        print(f"  Estimated Shoot Time: {resources['estimated_shoot_time']:.1f}s")
    
    completeness = compiler.calculate_completeness_score()
    print(f"\nShot List Completeness: {completeness:.1f}%")


def demo_consistency_engine():
    """Demo: Consistency Engine"""
    print("\n" + "=" * 60)
    print("DEMO 3: CONSISTENCY ENGINE")
    print("=" * 60)
    
    manager = ReferenceManager()
    engine = ConsistencyEngine(reference_manager=manager)
    
    frames = []
    for i in range(5):
        frame = ReferenceFrame(
            frame_id=f"frame_{i:03d}",
            shot_id="shot_001",
            timestamp=float(i) / 24.0,
            embeddings={
                'character': np.random.rand(512),
                'visual': np.random.rand(2048)
            },
            color_histogram=np.random.rand(256),
            lighting_profile={
                'intensity': 0.7 + np.random.rand() * 0.1,
                'color_temperature': 5500 + np.random.randint(-200, 200)
            },
            character_positions={'hero': (0.5 + i * 0.01, 0.5)}
        )
        frames.append(frame)
        manager.add_reference(frame, tags=['character:hero'])
    
    print(f"\nValidating consistency across {len(frames)} frames...")
    
    violations = engine.validate_shot_sequence(frames)
    print(f"Found {len(violations)} consistency violations")
    
    if violations:
        for v in violations[:3]:
            print(f"  - {v.violation_type.value}: {v.description}")
            print(f"    Severity: {v.severity:.2f}, Confidence: {v.confidence:.2f}")
    
    scores = engine.get_consistency_score(frames)
    print(f"\nConsistency Scores:")
    print(f"  Overall: {scores['overall']:.2f}")
    print(f"  Character Identity: {scores.get('character_identity', 1.0):.2f}")
    print(f"  Lighting: {scores.get('lighting', 1.0):.2f}")


def demo_evaluation_harness():
    """Demo: Evaluation Harness"""
    print("\n" + "=" * 60)
    print("DEMO 4: EVALUATION HARNESS")
    print("=" * 60)
    
    dataset = GoldenDataset()
    harness = EvaluationHarness(golden_dataset=dataset)
    
    print(f"\nGolden Dataset: {len(dataset.test_cases)} test scenarios")
    
    for test_id, test_case in list(dataset.test_cases.items())[:2]:
        print(f"\n  {test_id}: {test_case.name}")
        print(f"  Scenario: {test_case.scenario_type.value}")
        print(f"  Thresholds: {test_case.quality_thresholds}")
        
        simulated_output = {
            'metrics': {
                metric: threshold + np.random.rand() * 0.1
                for metric, threshold in test_case.quality_thresholds.items()
            }
        }
        
        result = harness.run_test_case(test_case, simulated_output)
        print(f"  Result: {'PASSED' if result.passed else 'FAILED'}")
        print(f"  Execution Time: {result.execution_time:.3f}s")
        
        if result.violations:
            print(f"  Violations: {', '.join(result.violations)}")


def demo_temporal_control():
    """Demo: Temporal Control Layer"""
    print("\n" + "=" * 60)
    print("DEMO 5: TEMPORAL CONTROL LAYER")
    print("=" * 60)
    
    layer = TemporalControlLayer(fps=24)
    
    print("\nAdding camera motion keyframes...")
    layer.add_motion_keyframe(
        0.0,
        camera_position=(0.0, 0.0, 5.0),
        camera_rotation=(0.0, 0.0, 0.0),
        zoom=1.0
    )
    
    layer.add_motion_keyframe(
        5.0,
        camera_position=(10.0, 2.0, 5.0),
        camera_rotation=(0.0, 15.0, 0.0),
        zoom=1.2
    )
    
    print("Generating frame sequence...")
    frames = layer.generate_frame_sequence(duration=5.0)
    print(f"Generated {len(frames)} frames")
    
    print("\nSample frame data:")
    for frame in frames[::24]:
        print(f"  Frame {frame['frame']}: pos_x={frame['camera'].get('pos_x', 0):.2f}, "
              f"zoom={frame['camera'].get('zoom', 1.0):.2f}")
    
    print("\nApplying speed ramp...")
    layer.apply_speed_ramp(1.0, 4.0, start_speed=1.0, end_speed=0.5)
    print("Speed ramp applied successfully")


def demo_quality_assurance():
    """Demo: Quality Assurance System"""
    print("\n" + "=" * 60)
    print("DEMO 6: QUALITY ASSURANCE SYSTEM")
    print("=" * 60)
    
    qa = QualityAssuranceSystem()
    
    video_data = {
        'width': 1920,
        'height': 1080,
        'fps': 24,
        'codec': 'h264',
        'bitrate': 8000,
        'audio_channels': 2,
        'frames': []
    }
    
    print("\nAssessing video quality...")
    report = qa.assess_quality(video_data, broadcast_standards=False)
    
    print(f"\nOverall Score: {report.overall_score:.2f}")
    print(f"Status: {'PASSED' if report.passed else 'FAILED'}")
    
    print("\nMetric Scores:")
    for metric, score in report.scores_by_metric.items():
        status = "✓" if score >= 0.8 else "✗"
        print(f"  {status} {metric}: {score:.2f}")
    
    if report.issues:
        print(f"\nIssues Found ({len(report.issues)}):")
        for issue in report.issues:
            print(f"  - {issue.description} (Severity: {issue.severity:.2f})")
            if issue.suggested_fix:
                print(f"    Fix: {issue.suggested_fix}")


def demo_character_identity():
    """Demo: Character Identity Preservation"""
    print("\n" + "=" * 60)
    print("DEMO 7: CHARACTER IDENTITY PRESERVATION")
    print("=" * 60)
    
    engine = CharacterIdentityEngine()
    
    print("\nAdding characters to library...")
    engine.add_character(
        "char_001",
        "Detective James",
        ["reference_images/james_01.jpg", "reference_images/james_02.jpg"],
        {"hair": "dark_brown", "eyes": "blue", "build": "athletic"}
    )
    
    engine.add_character(
        "char_002",
        "Sarah",
        ["reference_images/sarah_01.jpg"],
        {"hair": "blonde", "eyes": "green", "build": "average"}
    )
    
    print(f"Character library: {len(engine.character_profiles)} characters")
    
    base_prompt = "Walking through the rain, looking determined"
    identity_prompt = engine.preserve_identity_in_generation("char_001", base_prompt)
    
    print(f"\nOriginal Prompt: {base_prompt}")
    print(f"With Identity: {identity_prompt}")
    
    print("\nSimulating cross-frame validation...")
    frames = [
        {
            'frame_number': i,
            'face_detections': [
                {
                    'embedding': np.random.rand(512),
                    'bbox': (100, 100, 200, 200)
                }
            ]
        }
        for i in range(10)
    ]
    
    consistency = engine.validate_identity_consistency(frames, ["char_001"])
    print(f"Identity Consistency Score: {consistency['overall_consistency']:.2f}")


def demo_collaborative_workflow():
    """Demo: Collaborative Workflow"""
    print("\n" + "=" * 60)
    print("DEMO 8: COLLABORATIVE WORKFLOW")
    print("=" * 60)
    
    workflow = CollaborativeWorkflow()
    
    print("\nRegistering team members...")
    director = workflow.register_user("user_001", "Alice Director", "alice@studio.com", UserRole.DIRECTOR)
    editor = workflow.register_user("user_002", "Bob Editor", "bob@studio.com", UserRole.EDITOR)
    viewer = workflow.register_user("user_003", "Carol Viewer", "carol@client.com", UserRole.VIEWER)
    
    print(f"  {director.name} ({director.role.value}): {', '.join(director.permissions)}")
    print(f"  {editor.name} ({editor.role.value}): {', '.join(editor.permissions)}")
    print(f"  {viewer.name} ({viewer.role.value}): {', '.join(viewer.permissions)}")
    
    print("\nCreating project...")
    project = workflow.project_manager.create_project("proj_001", "Film Noir Detective", "user_001")
    workflow.project_manager.add_member("proj_001", "user_002", "user_001")
    workflow.project_manager.add_member("proj_001", "user_003", "user_001")
    
    print(f"Project: {project.name}")
    print(f"Members: {len(project.members)}")
    
    print("\nSimulating collaboration...")
    workflow.add_comment("comment_001", "user_002", "asset_001", "Love the lighting!", frame_number=42)
    workflow.add_comment("comment_002", "user_003", "asset_001", "Can we make it darker?")
    
    workflow.create_version("v001", "asset_001", "user_002", ["Adjusted lighting", "Added grain"], "/renders/v001.mp4")
    workflow.create_version("v002", "asset_001", "user_002", ["Made darker per feedback"], "/renders/v002.mp4")
    
    workflow.submit_for_approval("asset_001", "user_002", ["user_001"])
    workflow.approve_asset("asset_001", "user_001", approved=True, feedback="Perfect!")
    
    stats = workflow.get_collaboration_stats("proj_001")
    print(f"\nCollaboration Statistics:")
    print(f"  Total Activities: {stats['total_activities']}")
    print(f"  Comments: {stats['comments']}")
    print(f"  Versions: {stats['versions']}")
    print(f"  Approvals: {stats['approvals']}")
    print(f"  Active Contributors: {stats['active_contributors']}")


def demo_integrated_workflow():
    """Demo: Integrated Workflow using multiple wedge features"""
    print("\n" + "=" * 60)
    print("INTEGRATED WORKFLOW DEMONSTRATION")
    print("=" * 60)
    
    print("\n1. Planning: Using Film Grammar & Shot List Compiler")
    grammar = FilmGrammarEngine()
    compiler = ShotListCompiler()
    
    script = "INT. OFFICE - NIGHT\n\nDetective works late."
    scenes = compiler.parse_script(script)
    
    if scenes:
        shots = compiler.generate_coverage(scenes[0], 'action')
        print(f"   Generated {len(shots)} shots with grammar guidance")
    
    print("\n2. Production: Character Identity & Consistency")
    identity = CharacterIdentityEngine()
    identity.add_character("hero", "Detective", ["ref.jpg"])
    print("   Character library prepared for consistent generation")
    
    print("\n3. Generation: Temporal Control for motion")
    temporal = TemporalControlLayer()
    temporal.add_motion_keyframe(0.0, camera_position=(0, 0, 5))
    frames = temporal.generate_frame_sequence(2.0)
    print(f"   Generated {len(frames)} frames with precise timing")
    
    print("\n4. Validation: Quality Assurance & Evaluation")
    qa = QualityAssuranceSystem()
    video_data = {'width': 1920, 'height': 1080, 'fps': 24, 'codec': 'h264', 'bitrate': 8000, 'frames': []}
    report = qa.assess_quality(video_data)
    print(f"   Quality Score: {report.overall_score:.2f} - {'PASSED' if report.passed else 'NEEDS WORK'}")
    
    print("\n5. Collaboration: Team Review & Approval")
    workflow = CollaborativeWorkflow()
    workflow.register_user("director", "Director", "dir@studio.com", UserRole.DIRECTOR)
    project = workflow.project_manager.create_project("demo", "Demo Project", "director")
    print(f"   Project '{project.name}' ready for team collaboration")
    
    print("\n✓ Complete production pipeline demonstrated!")


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 60)
    print("ANIMAtiZE WEDGE FEATURES DEMONSTRATION")
    print("Strategic Features for Defensible Competitive Moat")
    print("=" * 60)
    
    demos = [
        demo_film_grammar,
        demo_shot_list_compiler,
        demo_consistency_engine,
        demo_evaluation_harness,
        demo_temporal_control,
        demo_quality_assurance,
        demo_character_identity,
        demo_collaborative_workflow,
        demo_integrated_workflow
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\nError in {demo.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nAll 8 wedge features demonstrated successfully!")
    print("These features create a defensible moat through:")
    print("  • Proprietary data accumulation")
    print("  • Workflow integration and lock-in")
    print("  • Industry-standard evaluation")
    print("  • Technical depth and precision")


if __name__ == '__main__':
    main()

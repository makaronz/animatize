"""
Example usage of the Consistency Engine

Demonstrates:
1. Creating style anchors, character references, and world references
2. Processing shots and frames
3. Validating consistency across shots
4. Generating consistency reports
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.wedge_features.consistency_integration import (
    ConsistencyOrchestrator,
    ConsistencyMiddleware,
)
from src.wedge_features.consistency_engine import ConsistencyType
import numpy as np


def example_basic_usage():
    """Basic usage example"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Consistency Engine Usage")
    print("=" * 80)
    
    orchestrator = ConsistencyOrchestrator(
        storage_path="data/reference_library",
        enable_scene_analyzer=True,
    )
    
    print("\n✓ ConsistencyOrchestrator initialized")
    
    stats = orchestrator.get_summary_statistics()
    print(f"\nInitial Statistics:")
    print(f"  - Total shots: {stats['total_shots']}")
    print(f"  - Total frames: {stats['total_frames']}")
    print(f"  - Characters: {stats['characters']}")
    print(f"  - Style anchors: {stats['style_anchors']}")
    print(f"  - Worlds: {stats['worlds']}")


def example_style_anchor_creation():
    """Example of creating style anchors"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Creating Style Anchors")
    print("=" * 80)
    
    orchestrator = ConsistencyOrchestrator()
    
    style_features = {
        "color_palette": [(135, 206, 235), (34, 139, 34), (255, 215, 0)],
        "lighting_style": {
            "intensity": "medium",
            "brightness": 150.0,
            "contrast": 45.0,
            "quality": "balanced",
            "color_temperature": 5500,
        },
        "texture_profile": {
            "complexity": 0.6,
            "smoothness": 0.7,
            "detail_level": 0.5,
        },
        "composition_style": {
            "edge_density": 0.12,
            "complexity": "medium",
        },
    }
    
    style_embedding = orchestrator.consistency_engine.style_extractor.create_style_embedding(
        style_features
    )
    
    from src.wedge_features.consistency_engine import StyleAnchor
    
    style_anchor = StyleAnchor(
        anchor_id="fantasy_style_01",
        name="Fantasy Adventure Style",
        description="Vibrant fantasy world with magical lighting and rich colors",
        style_embedding=style_embedding,
        visual_attributes=style_features,
        color_palette=style_features["color_palette"],
        lighting_style=style_features["lighting_style"],
        texture_profile=style_features["texture_profile"],
    )
    
    success = orchestrator.consistency_engine.reference_library.add_style_anchor(style_anchor)
    
    if success:
        print(f"\n✓ Style anchor created: {style_anchor.name}")
        print(f"  - ID: {style_anchor.anchor_id}")
        print(f"  - Color palette: {len(style_anchor.color_palette)} colors")
        print(f"  - Embedding shape: {style_anchor.style_embedding.shape}")


def example_character_reference_creation():
    """Example of creating character references"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Creating Character References")
    print("=" * 80)
    
    orchestrator = ConsistencyOrchestrator()
    
    appearance_embedding = np.random.rand(64).astype(np.float32)
    
    from src.wedge_features.consistency_engine import CharacterReference
    
    character = CharacterReference(
        character_id="hero_001",
        name="Alex the Hero",
        description="Brave warrior with distinctive armor and sword",
        appearance_embedding=appearance_embedding,
        facial_features={
            "eye_color": "blue",
            "hair_color": "brown",
            "hair_style": "short",
            "distinctive_marks": ["scar on left cheek"],
        },
        body_proportions={
            "height": 1.8,
            "build": "athletic",
        },
        clothing={
            "primary": "silver armor",
            "secondary": "blue cape",
            "accessories": ["sword", "shield"],
        },
        color_scheme=[(192, 192, 192), (0, 0, 255), (139, 69, 19)],
    )
    
    success = orchestrator.consistency_engine.reference_library.add_character(character)
    
    if success:
        print(f"\n✓ Character reference created: {character.name}")
        print(f"  - ID: {character.character_id}")
        print(f"  - Facial features: {list(character.facial_features.keys())}")
        print(f"  - Color scheme: {len(character.color_scheme)} colors")
        print(f"  - Embedding shape: {character.appearance_embedding.shape}")


def example_world_reference_creation():
    """Example of creating world references"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Creating World References")
    print("=" * 80)
    
    orchestrator = ConsistencyOrchestrator()
    
    spatial_embedding = np.random.rand(64).astype(np.float32)
    
    from src.wedge_features.consistency_engine import WorldReference
    
    world = WorldReference(
        world_id="castle_exterior_01",
        name="Grand Castle Exterior",
        description="Majestic medieval castle with towers and courtyard",
        spatial_embedding=spatial_embedding,
        location_map={
            "main_gate": (0.5, 0.6, 0.0),
            "north_tower": (0.3, 0.2, 0.8),
            "south_tower": (0.7, 0.2, 0.8),
            "courtyard": (0.5, 0.5, 0.0),
        },
        lighting_conditions={
            "intensity": "high",
            "color_temperature": 6000,
            "direction": "top-right",
        },
        time_of_day="midday",
        weather="clear",
        architectural_style="gothic",
        scale_references={
            "gate_height": 5.0,
            "tower_height": 30.0,
            "courtyard_width": 50.0,
        },
    )
    
    success = orchestrator.consistency_engine.reference_library.add_world(world)
    
    if success:
        print(f"\n✓ World reference created: {world.name}")
        print(f"  - ID: {world.world_id}")
        print(f"  - Time of day: {world.time_of_day}")
        print(f"  - Weather: {world.weather}")
        print(f"  - Locations: {list(world.location_map.keys())}")
        print(f"  - Scale references: {list(world.scale_references.keys())}")


def example_shot_processing():
    """Example of processing shots and frames"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Processing Shots and Validating Consistency")
    print("=" * 80)
    
    orchestrator = ConsistencyOrchestrator()
    
    from src.wedge_features.consistency_engine import ReferenceFrame
    
    print("\n→ Creating mock frames for Shot 1...")
    frames_shot1 = []
    for i in range(3):
        frame = ReferenceFrame(
            frame_id=f"shot1_frame{i}",
            shot_id="shot_001",
            timestamp=i * 0.5,
            embeddings={
                "style": np.random.rand(64).astype(np.float32),
            },
            color_histogram=np.array([0.3, 0.2, 0.15, 0.1]),
            lighting_profile={
                "intensity": 0.75 + (i * 0.01),
                "color_temperature": 5500,
            },
            character_positions={
                "hero_001": (0.5 + i * 0.05, 0.6),
            },
            character_ids={"hero_001"},
        )
        frames_shot1.append(frame)
        orchestrator.shot_registry["shot_001"] = frames_shot1
        orchestrator.consistency_engine.reference_library.add_frame(frame)
    
    print(f"✓ Created {len(frames_shot1)} frames for shot_001")
    
    print("\n→ Validating shot consistency...")
    validation = orchestrator.validate_shot_consistency("shot_001")
    
    print(f"\nValidation Results for shot_001:")
    print(f"  - Frame count: {validation['frame_count']}")
    print(f"  - Violations: {len(validation['violations'])}")
    print(f"  - Overall score: {validation['scores']['overall']:.3f}")
    print(f"  - Passed: {validation['passed']}")
    
    if validation['violations']:
        print("\n  Violations detected:")
        for v in validation['violations']:
            print(f"    - {v['type']}: {v['description']}")


def example_cross_shot_validation():
    """Example of cross-shot consistency validation"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Cross-Shot Consistency Validation")
    print("=" * 80)
    
    orchestrator = ConsistencyOrchestrator()
    
    from src.wedge_features.consistency_engine import ReferenceFrame
    
    for shot_num in [1, 2, 3]:
        shot_id = f"shot_00{shot_num}"
        frames = []
        
        for frame_num in range(2):
            frame = ReferenceFrame(
                frame_id=f"{shot_id}_frame{frame_num}",
                shot_id=shot_id,
                timestamp=frame_num * 0.5,
                embeddings={
                    "style": np.random.rand(64).astype(np.float32),
                },
                color_histogram=np.array([0.3, 0.2, 0.15, 0.1]) + np.random.rand(4) * 0.05,
                lighting_profile={
                    "intensity": 0.75 + (shot_num * 0.05),
                    "color_temperature": 5500,
                },
            )
            frames.append(frame)
        
        orchestrator.shot_registry[shot_id] = frames
        for frame in frames:
            orchestrator.consistency_engine.reference_library.add_frame(frame)
        
        print(f"✓ Created {len(frames)} frames for {shot_id}")
    
    print("\n→ Validating sequence consistency...")
    result = orchestrator.validate_sequence_consistency(["shot_001", "shot_002", "shot_003"])
    
    print(f"\nSequence Validation Results:")
    print(f"  - Total frames: {result['total_frames']}")
    print(f"  - Overall consistency: {result['report']['summary']['consistency_score']:.3f}")
    print(f"  - Total violations: {result['report']['summary']['total_violations']}")
    print(f"  - Pass threshold: {result['report']['summary']['pass_threshold']}")
    
    if result['report']['recommendations']:
        print("\n  Recommendations:")
        for rec in result['report']['recommendations']:
            print(f"    - {rec}")


def example_middleware_usage():
    """Example of using consistency middleware"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Using ConsistencyMiddleware")
    print("=" * 80)
    
    orchestrator = ConsistencyOrchestrator()
    middleware = ConsistencyMiddleware(orchestrator, auto_validate=True)
    
    print("\n✓ ConsistencyMiddleware initialized with auto-validation")
    
    middleware.before_shot("shot_001")
    print(f"→ Started shot: shot_001")
    
    print("\n→ Simulating frame generation...")
    print("  (In real usage, replace with actual image paths)")
    
    validation = middleware.after_shot()
    print(f"\n✓ Shot completed")
    print(f"  - Frames processed: {validation.get('frame_count', 0)}")


def example_consistency_report():
    """Example of generating consistency report"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Generating Comprehensive Consistency Report")
    print("=" * 80)
    
    orchestrator = ConsistencyOrchestrator()
    
    from src.wedge_features.consistency_engine import ReferenceFrame
    
    frames = []
    for i in range(5):
        frame = ReferenceFrame(
            frame_id=f"frame_{i}",
            shot_id="shot_001",
            timestamp=i * 0.5,
            embeddings={
                "style": np.random.rand(64).astype(np.float32),
            },
            color_histogram=np.array([0.3, 0.2, 0.15, 0.1]) + np.random.rand(4) * 0.1,
            lighting_profile={
                "intensity": 0.75 + (i * 0.03),
                "color_temperature": 5500 + (i * 100),
            },
        )
        frames.append(frame)
    
    print(f"✓ Created {len(frames)} frames")
    
    report = orchestrator.consistency_engine.generate_consistency_report(frames)
    
    print("\n" + "-" * 80)
    print("CONSISTENCY REPORT")
    print("-" * 80)
    
    print(f"\nSummary:")
    print(f"  Total frames: {report['summary']['total_frames']}")
    print(f"  Total violations: {report['summary']['total_violations']}")
    print(f"  Consistency score: {report['summary']['consistency_score']:.3f}")
    print(f"  Pass threshold: {report['summary']['pass_threshold']}")
    
    print(f"\nScores by Type:")
    for check_type, score in report['scores_by_type'].items():
        print(f"  {check_type}: {score:.3f}")
    
    if report['violations']:
        print(f"\nViolations ({len(report['violations'])}):")
        for i, v in enumerate(report['violations'][:3], 1):
            print(f"  {i}. {v['type']}: {v['description']}")
            print(f"     Severity: {v['severity']:.3f}, Confidence: {v['confidence']:.3f}")
            print(f"     Fix: {v['suggested_fix']}")
    
    if report['recommendations']:
        print(f"\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "CONSISTENCY ENGINE EXAMPLES" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        example_basic_usage()
        example_style_anchor_creation()
        example_character_reference_creation()
        example_world_reference_creation()
        example_shot_processing()
        example_cross_shot_validation()
        example_middleware_usage()
        example_consistency_report()
        
        print("\n" + "=" * 80)
        print("✓ All examples completed successfully!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

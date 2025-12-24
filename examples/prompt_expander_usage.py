#!/usr/bin/env python3
"""
Prompt Expander Usage Example
Demonstrates how to use the ANIMAtiZE prompt expander module
including Director Intent compilation and control map system
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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
    SeedManager
)
import json


def example_simple_expansion():
    """Example 1: Simple prompt expansion"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set - skipping GPT expansion example")
        return
    
    expander = PromptExpander(api_key=api_key)
    
    print("=" * 60)
    print("Example 1: Simple Prompt Expansion with GPT")
    print("=" * 60)
    
    request = ExpansionRequest(
        base_prompt="A hero walking towards the camera in slow motion",
        rules=[
            {
                "id": "rule_001",
                "name": "Hero Shot",
                "snippet": "dramatic low angle emphasizing power and presence",
                "priority": 0.9
            },
            {
                "id": "rule_002",
                "name": "Slow Motion",
                "snippet": "120fps capture for smooth slow motion",
                "priority": 0.8
            }
        ],
        context={"mood": "epic", "lighting": "backlit"}
    )
    
    result = expander.expand_prompt(request)
    print(f"\n✅ Expansion Complete")
    print(f"Original: {request.base_prompt}")
    print(f"Expanded: {result.expanded_prompt}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Time: {result.processing_time:.2f}s")


def example_director_intent_compilation():
    """Example 2: Director Intent to Model-Specific Prompts"""
    print("\n" + "=" * 60)
    print("Example 2: Director Intent Compilation")
    print("=" * 60)
    
    expander = PromptExpander()
    
    determinism = DeterminismConfig(
        use_fixed_seed=True,
        seed=42,
        reproducibility_level="high"
    )
    
    camera_motion = CameraMotion(
        motion_type=CameraMotionType.DOLLY_IN,
        strength=MotionStrength.MODERATE,
        speed=0.8,
        easing="ease_in_out"
    )
    
    character = CharacterConsistency(
        character_id="protagonist",
        reference_frames=[0, 10, 20],
        feature_weights={"face": 1.0, "body": 0.8, "clothing": 0.9},
        appearance_locked=True
    )
    
    shot1 = Shot(
        shot_id="shot_001",
        scene_id="scene_001",
        prompt="Wide establishing shot of a futuristic city at sunset",
        camera_motion=camera_motion,
        fps=24,
        duration=8.0,
        motion_strength=MotionStrength.SUBTLE
    )
    
    shot2 = Shot(
        shot_id="shot_002",
        scene_id="scene_001",
        prompt="Close-up of protagonist looking at the city skyline",
        characters=[character],
        fps=24,
        duration=5.0,
        motion_strength=MotionStrength.SUBTLE
    )
    
    transition = ShotTransition(
        from_shot="shot_001",
        to_shot="shot_002",
        transition_type=TransitionType.DISSOLVE,
        duration=1.0
    )
    
    scene = Scene(
        scene_id="scene_001",
        description="Opening scene establishing the world",
        shots=[shot1, shot2],
        transitions=[transition],
        scene_fps=24,
        total_duration=13.0
    )
    
    intent = DirectorIntent(
        intent_id="film_001",
        narrative_description="A sci-fi epic about humanity's future",
        style_references=["Blade Runner 2049", "Dune"],
        mood="contemplative",
        visual_theme="neo-noir cyberpunk",
        target_providers=["runway", "pika", "sora"],
        scenes=[scene],
        global_determinism=determinism,
        prompt_version=PromptVersion.V2_0,
        schema_version=SchemaVersion.V3_0
    )
    
    result = expander.compile_director_intent(intent)
    
    print(f"\n✅ Compilation Complete")
    print(f"Intent ID: {result.intent_id}")
    print(f"Compilation Time: {result.compilation_time:.3f}s")
    print(f"Scenes: {result.compilation_metadata['num_scenes']}")
    print(f"Shots: {result.compilation_metadata['num_shots']}")
    print(f"\nGenerated {len(result.model_prompts)} model-specific prompts:")
    
    for prompt in result.model_prompts:
        print(f"\n  🎬 Provider: {prompt.provider} ({prompt.model})")
        print(f"     Prompt: {prompt.compiled_prompt[:80]}...")
        print(f"     Controls: {list(prompt.control_parameters.keys())}")
    
    print(f"\n🔢 Seed Manifest (for reproducibility):")
    for context, seed in list(result.seed_manifest.items())[:3]:
        print(f"  {context}: {seed}")
    
    if result.warnings:
        print(f"\n⚠️  Warnings: {result.warnings}")


def example_multi_scene_production():
    """Example 3: Multi-Scene Production with Storyboards"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Scene Production with Shot List")
    print("=" * 60)
    
    expander = PromptExpander()
    
    storyboard1 = Storyboard(
        panel_id="panel_001",
        shot_number="1A",
        description="Hero stands on cliff overlooking valley",
        camera_angle="low angle",
        composition="rule of thirds, hero on right",
        duration=3.0
    )
    
    storyboard2 = Storyboard(
        panel_id="panel_002",
        shot_number="1B",
        description="POV shot of the vast valley below",
        camera_angle="eye level",
        composition="centered horizon",
        duration=2.0
    )
    
    scene1_shot1 = Shot(
        shot_id="s1_shot_001",
        scene_id="scene_001",
        prompt="Epic landscape with hero silhouetted against sunset",
        camera_motion=CameraMotion(
            motion_type=CameraMotionType.CRANE_UP,
            strength=MotionStrength.MODERATE,
            speed=0.5
        ),
        fps=24,
        duration=5.0,
        storyboard_ref="panel_001"
    )
    
    scene1 = Scene(
        scene_id="scene_001",
        description="Opening establishing shots",
        shots=[scene1_shot1],
        scene_fps=24
    )
    
    scene2_shot1 = Shot(
        shot_id="s2_shot_001",
        scene_id="scene_002",
        prompt="Hero begins journey down mountain path",
        camera_motion=CameraMotion(
            motion_type=CameraMotionType.TRACK_RIGHT,
            strength=MotionStrength.MODERATE,
            speed=1.0
        ),
        fps=24,
        duration=6.0
    )
    
    scene2 = Scene(
        scene_id="scene_002",
        description="Hero's journey begins",
        shots=[scene2_shot1],
        scene_fps=24
    )
    
    intent = DirectorIntent(
        intent_id="epic_journey",
        narrative_description="Hero's journey across mystical lands",
        style_references=["Lord of the Rings", "The Witcher"],
        mood="adventurous",
        visual_theme="epic fantasy",
        target_providers=["runway", "veo"],
        scenes=[scene1, scene2],
        storyboards=[storyboard1, storyboard2],
        global_determinism=DeterminismConfig(seed=12345, use_fixed_seed=True)
    )
    
    result = expander.compile_director_intent(intent)
    
    print(f"\n✅ Multi-Scene Production Compiled")
    print(f"Total Scenes: {len(result.scene_breakdown)}")
    print(f"Total Shots: {len(result.shot_list)}")
    print(f"Storyboards: {len(intent.storyboards)}")
    print(f"Providers: {', '.join(intent.target_providers)}")
    
    print(f"\n📋 Shot List:")
    for shot in result.shot_list:
        print(f"  • {shot.shot_id}: {shot.prompt[:60]}...")
        if shot.camera_motion:
            print(f"    📷 Camera: {shot.camera_motion.motion_type.value} ({shot.camera_motion.strength.value})")
        print(f"    ⏱️  Duration: {shot.duration}s @ {shot.fps}fps")


def example_control_vocabulary():
    """Example 4: Control Vocabulary and Validation"""
    print("\n" + "=" * 60)
    print("Example 4: Control Vocabulary Reference")
    print("=" * 60)
    
    vocab = ControlVocabulary.get_vocabulary()
    
    print("\n📹 Camera Motion Types:")
    for motion in vocab['camera_motion']['types'][:10]:
        print(f"  • {motion}")
    print(f"  ... and {len(vocab['camera_motion']['types']) - 10} more")
    
    print("\n💪 Motion Strength Levels:")
    for strength in vocab['motion_strength']:
        print(f"  • {strength}")
    
    print("\n🎞️  Supported FPS Values:")
    print(f"  {', '.join(map(str, vocab['fps']))}")
    
    print("\n🎨 Control Map Types:")
    for map_type in vocab['control_maps']['types']:
        print(f"  • {map_type}")
    
    print("\n✂️  Shot Transitions:")
    for transition in vocab['shot_transitions']:
        print(f"  • {transition}")


def example_determinism_and_seeds():
    """Example 5: Seed Management for Reproducibility"""
    print("\n" + "=" * 60)
    print("Example 5: Determinism and Seed Management")
    print("=" * 60)
    
    seed_manager = SeedManager(base_seed=42)
    
    seed1 = seed_manager.generate_seed("scene_001:shot_001")
    seed2 = seed_manager.generate_seed("scene_001:shot_002")
    seed3 = seed_manager.generate_seed("scene_002:shot_001")
    
    print("\n🎲 Generated Seeds:")
    print(f"  scene_001:shot_001 → {seed1}")
    print(f"  scene_001:shot_002 → {seed2}")
    print(f"  scene_002:shot_001 → {seed3}")
    
    manifest = seed_manager.export_manifest()
    print(f"\n📄 Seed Manifest (for reproducibility):")
    print(json.dumps(manifest, indent=2))
    
    new_manager = SeedManager()
    new_manager.import_manifest(manifest)
    
    reproduced_seed = new_manager.get_or_create_seed("scene_001:shot_001")
    print(f"\n✅ Reproduced seed matches: {seed1 == reproduced_seed}")


def example_character_consistency():
    """Example 6: Character Consistency Across Shots"""
    print("\n" + "=" * 60)
    print("Example 6: Character Consistency Control")
    print("=" * 60)
    
    expander = PromptExpander()
    
    protagonist = CharacterConsistency(
        character_id="hero_main",
        reference_frames=[0, 15, 30],
        feature_weights={
            "face": 1.0,
            "body": 0.9,
            "clothing": 0.95,
            "hair": 0.85
        },
        appearance_locked=True,
        expression_range=("neutral", "determined"),
        clothing_consistency=True
    )
    
    ref_frame = ReferenceFrame(
        frame_id="ref_001",
        timestamp=0.0,
        image_path="/path/to/character_reference.jpg",
        weight=1.0,
        aspect="full"
    )
    
    shot_with_character = Shot(
        shot_id="char_shot_001",
        scene_id="scene_003",
        prompt="Hero walks through medieval village marketplace",
        characters=[protagonist],
        reference_frames=[ref_frame],
        fps=24,
        duration=4.0
    )
    
    print(f"\n👤 Character Configuration:")
    print(f"  ID: {protagonist.character_id}")
    print(f"  Appearance Locked: {protagonist.appearance_locked}")
    print(f"  Feature Weights: {protagonist.feature_weights}")
    print(f"  Reference Frames: {len(shot_with_character.reference_frames)}")
    print(f"\n✅ Character consistency will be maintained across shots")


def example_control_maps():
    """Example 7: Control Maps for Spatial Guidance"""
    print("\n" + "=" * 60)
    print("Example 7: Control Maps for Spatial Guidance")
    print("=" * 60)
    
    depth_map = ControlMap(
        map_type="depth",
        map_data="/path/to/depth_map.png",
        strength=0.8,
        start_frame=0,
        end_frame=120,
        preprocessor="depth_midas",
        conditioning_scale=1.0
    )
    
    pose_map = ControlMap(
        map_type="pose",
        map_data="/path/to/pose_sequence.json",
        strength=1.0,
        start_frame=0,
        end_frame=120,
        preprocessor="openpose",
        conditioning_scale=0.9
    )
    
    shot_with_controls = Shot(
        shot_id="controlled_shot_001",
        scene_id="scene_004",
        prompt="Dancer performs choreographed routine",
        control_maps=[depth_map, pose_map],
        fps=30,
        duration=4.0
    )
    
    print(f"\n🎛️  Control Maps Applied:")
    for i, ctrl_map in enumerate(shot_with_controls.control_maps, 1):
        print(f"  {i}. Type: {ctrl_map.map_type}")
        print(f"     Strength: {ctrl_map.strength}")
        print(f"     Frames: {ctrl_map.start_frame}-{ctrl_map.end_frame}")
        print(f"     Preprocessor: {ctrl_map.preprocessor}")


def main():
    """Run all examples"""
    print("\n🎬 ANIMAtiZE Prompt Compiler & Control Map System")
    print("=" * 60)
    print("Comprehensive examples of Director Intent compilation\n")
    
    try:
        example_director_intent_compilation()
        example_multi_scene_production()
        example_control_vocabulary()
        example_determinism_and_seeds()
        example_character_consistency()
        example_control_maps()
        
        if os.getenv("OPENAI_API_KEY"):
            example_simple_expansion()
        else:
            print("\n" + "=" * 60)
            print("ℹ️  Set OPENAI_API_KEY to run GPT expansion examples")
            print("=" * 60)
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

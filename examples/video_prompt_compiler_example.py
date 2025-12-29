"""
Example: Enhanced Video Prompt Compiler with Video-Specific Controls

Demonstrates the new features:
- Video control parameters (camera_motion, duration, fps, shot_type, transitions, motion_strength)
- Versioning (prompt_version, schema_version)
- Integration with 47+ cinematic rules from movement_prediction_rules.json
- Determinism controls (seed management for reproducibility)
"""

import json
from src.generators.video_prompt_generator import (
    VideoPromptCompiler,
    VideoControlParameters,
    DeterminismConfig,
    VideoGenerationRequest,
    CameraMotion,
    ModelType,
)


def example_basic_compilation():
    """Example 1: Basic prompt compilation with automatic inference"""
    print("=" * 80)
    print("Example 1: Basic Prompt Compilation")
    print("=" * 80)

    compiler = VideoPromptCompiler()

    request = VideoGenerationRequest(
        model_type=ModelType.KLING,
        scene_description=(
            "A young woman in a flowing red dress walks through a misty forest at golden hour. "
            "Camera slowly dollies in to reveal her expression."
        ),
        duration=8.0,
        aspect_ratio="16:9",
        style="cinematic",
        temporal_consistency_priority="high",
    )

    compiled = compiler.compile_video_prompt(request)

    print(f"\nPrompt Text:\n{compiled.prompt_text}\n")
    print(f"Version: {compiled.version.prompt_version}")
    print(f"Schema: {compiled.version.schema_version}")
    print(f"Cinematic Rules Applied: {compiled.cinematic_rules.total_rules_applied}")
    print(f"Seed: {compiled.temporal_config.seed}")
    print(f"FPS: {compiled.control_parameters.fps}")
    print(f"Shot Type: {compiled.control_parameters.shot_type}")


def example_full_control():
    """Example 2: Full control with explicit parameters"""
    print("\n" + "=" * 80)
    print("Example 2: Full Control with Explicit Parameters")
    print("=" * 80)

    compiler = VideoPromptCompiler()

    # Define precise control parameters
    controls = VideoControlParameters(
        camera_motion=CameraMotion(type="dolly", speed="slow", direction="in", focal_length=50),
        duration_seconds=10.0,
        fps=24,
        shot_type="medium",
        transitions="fade",
        motion_strength=0.4,
    )

    # Configure determinism for reproducibility
    determinism = DeterminismConfig(seed=12345, enable_seed_management=True, seed_increment_per_scene=100)

    request = VideoGenerationRequest(
        model_type=ModelType.SORA2,
        scene_description="A warrior stands on a windswept cliff at sunrise, their cloak billowing dramatically",
        duration=10.0,
        aspect_ratio="16:9",
        style="epic cinematic",
        temporal_consistency_priority="critical",
        control_parameters=controls,
        determinism_config=determinism,
    )

    compiled = compiler.compile_video_prompt(request)
    params = compiler.compile_model_parameters(compiled)

    print(f"\nPrompt Text:\n{compiled.prompt_text}\n")
    print("\nControl Parameters:")
    print(json.dumps(compiled.control_parameters.to_dict(), indent=2))
    print("\nModel Parameters:")
    print(json.dumps(params, indent=2))
    print("\nCinematic Rules Applied:")
    for rule_name in compiled.cinematic_rules.rule_names[:5]:
        print(f"  - {rule_name}")


def example_multi_scene_coherence():
    """Example 3: Multi-scene compilation with coherence"""
    print("\n" + "=" * 80)
    print("Example 3: Multi-Scene Compilation with Coherence")
    print("=" * 80)

    compiler = VideoPromptCompiler()

    scenes = [
        "A lone astronaut floats in the void of space, Earth visible in the distance",
        "The astronaut reaches out towards a mysterious glowing object",
        "Close-up of the astronaut's face showing wonder and determination",
        "Wide shot as the astronaut propels towards the object",
    ]

    # Shared configuration for all scenes
    shared_config = VideoGenerationRequest(
        model_type=ModelType.RUNWAY,
        scene_description="",
        duration=6.0,
        aspect_ratio="16:9",
        style="sci-fi cinematic",
        temporal_consistency_priority="high",
        determinism_config=DeterminismConfig(seed=99999, enable_seed_management=True, seed_increment_per_scene=1000),
    )

    result = compiler.compile_multi_scene_prompts(scenes, ModelType.RUNWAY, shared_config)

    print(f"\nTotal Scenes: {result['total_scenes']}")
    print(f"Schema Version: {result['version']['schema_version']}")
    print(f"Compiler Version: {result['version']['compiler_version']}")

    print("\nCoherence Strategy:")
    print(f"  Base Seed: {result['coherence_strategy']['base_seed']}")
    print(f"  Seed Increment: {result['coherence_strategy']['seed_increment']}")

    print("\nConsistency Analysis:")
    print(f"  Character Consistency: {result['consistency_analysis']['character_consistency']}")
    print(f"  Style Uniformity: {result['consistency_analysis']['style_uniformity']}")
    print(f"  Average Rules Applied: {result['consistency_analysis']['average_rules_applied']:.1f}")

    print("\nScene Details:")
    for scene in result["scenes"]:
        scene_num = scene["scene_number"]
        seed = scene["compiled_prompt"]["temporal_config"]["seed"]
        rules = scene["compiled_prompt"]["cinematic_rules"]["total_rules_applied"]
        print(f"  Scene {scene_num}: Seed={seed}, Rules={rules}")


def example_determinism_strategies():
    """Example 4: Different determinism strategies"""
    print("\n" + "=" * 80)
    print("Example 4: Determinism Strategies")
    print("=" * 80)

    compiler = VideoPromptCompiler()

    base_request = VideoGenerationRequest(
        model_type=ModelType.KLING, scene_description="A mystical portal opens in an ancient temple", duration=5.0
    )

    # Strategy 1: Fixed seed
    print("\nStrategy 1: Fixed Seed")
    det1 = DeterminismConfig(seed=42, enable_seed_management=True)
    base_request.determinism_config = det1
    compiled1 = compiler.compile_video_prompt(base_request)
    print(f"  Seed: {compiled1.temporal_config.seed}")

    # Strategy 2: Hash-based seed (from prompt text)
    print("\nStrategy 2: Hash-Based Seed")
    det2 = DeterminismConfig(use_hash_based_seed=True)
    base_request.determinism_config = det2
    compiled2 = compiler.compile_video_prompt(base_request)
    print(f"  Seed: {compiled2.temporal_config.seed}")

    # Strategy 3: Incremental for multi-scene
    print("\nStrategy 3: Incremental Seeds for Multi-Scene")
    det3 = DeterminismConfig(seed=1000, seed_increment_per_scene=50)
    for i in range(3):
        base_request.determinism_config = det3
        compiled = compiler.compile_video_prompt(base_request, scene_index=i)
        print(f"  Scene {i+1} Seed: {compiled.temporal_config.seed}")


def example_cinematic_rules_integration():
    """Example 5: Cinematic rules integration"""
    print("\n" + "=" * 80)
    print("Example 5: Cinematic Rules Integration")
    print("=" * 80)

    compiler = VideoPromptCompiler()

    # Camera movement triggers specific rules
    controls = VideoControlParameters(
        camera_motion=CameraMotion(type="orbit", speed="slow"), shot_type="wide", motion_strength=0.3
    )

    request = VideoGenerationRequest(
        model_type=ModelType.LUMA,
        scene_description="A dancer performs in an empty theater, camera orbits gracefully",
        control_parameters=controls,
    )

    compiled = compiler.compile_video_prompt(request)

    print(f"\nCamera Motion: {controls.camera_motion.type}")
    print(f"Rules Applied: {compiled.cinematic_rules.total_rules_applied}")

    print("\nRule IDs:")
    for rule_id in compiled.cinematic_rules.rule_ids[:5]:
        print(f"  - {rule_id}")

    print("\nEnhancements:")
    for key, enhancement in compiled.cinematic_rules.enhancements.items():
        print(f"  {key}: {enhancement[:80]}...")


def example_export_import():
    """Example 6: Export compiled prompt for storage/transfer"""
    print("\n" + "=" * 80)
    print("Example 6: Export/Import Compiled Prompt")
    print("=" * 80)

    compiler = VideoPromptCompiler()

    request = VideoGenerationRequest(
        model_type=ModelType.VEO3,
        scene_description="A time-lapse of a city transforming from day to night",
        duration=7.0,
    )

    compiled = compiler.compile_video_prompt(request)

    # Export to dictionary (can be saved to JSON)
    exported = compiled.to_dict()

    print("\nExported Structure:")
    print(json.dumps(exported, indent=2)[:1000] + "...")

    print(f"\nExported Keys: {list(exported.keys())}")
    print(f"Prompt Version: {exported['version']['prompt_version']}")
    print(f"Schema Version: {exported['version']['schema_version']}")


def example_model_comparison():
    """Example 7: Same intent compiled for different models"""
    print("\n" + "=" * 80)
    print("Example 7: Model-Specific Compilation")
    print("=" * 80)

    compiler = VideoPromptCompiler()

    intent = "A phoenix rises from flames, spreading its majestic wings"

    models = [ModelType.KLING, ModelType.SORA2, ModelType.RUNWAY]

    for model in models:
        request = VideoGenerationRequest(model_type=model, scene_description=intent, duration=5.0)

        compiled = compiler.compile_video_prompt(request)

        print(f"\n{model.value.upper()}:")
        print(f"  Prompt: {compiled.prompt_text[:100]}...")
        print(f"  Rules Applied: {compiled.cinematic_rules.total_rules_applied}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "ENHANCED VIDEO PROMPT COMPILER EXAMPLES" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")

    example_basic_compilation()
    example_full_control()
    example_multi_scene_coherence()
    example_determinism_strategies()
    example_cinematic_rules_integration()
    example_export_import()
    example_model_comparison()

    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80 + "\n")

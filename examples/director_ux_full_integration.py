"""
Director UX Full Integration Example

Demonstrates complete integration of Director UX with ANIMAtiZE framework,
showing the full pipeline from UX controls to model-specific video generation.
"""

import json
from src.core.director_ux import (
    DirectorControls,
    DirectorMode,
    CameraMovementType,
    ShotType,
    MotionStrengthLevel,
    StylePreset,
    PresetLibrary,
    IterationWorkflow,
    AutoModeAssistant,
    GenerationComparison
)
from src.core.prompt_expander import (
    PromptCompiler,
    DirectorIntent,
    Scene,
    Shot,
    CameraMotion,
    MotionStrength,
    CameraMotionType,
    DeterminismConfig
)


def example_1_simple_commercial():
    """Example 1: Simple commercial video generation"""
    print("=" * 70)
    print("EXAMPLE 1: Simple Commercial Video")
    print("=" * 70)
    
    # Step 1: Use preset
    print("\n1. Loading Commercial preset...")
    controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
    
    # Step 2: Customize
    print("2. Customizing for product showcase...")
    controls.timing.duration = 7.0
    controls.mood = "luxury"
    
    # Step 3: Convert to internal parameters
    print("3. Converting to internal parameters...")
    internal_params = controls.to_internal_params()
    
    print("\nGenerated Parameters:")
    print(f"  Camera: {internal_params['camera_motion']['type']}")
    print(f"  Shot Type: {internal_params['shot_type']}")
    print(f"  Duration: {internal_params['duration']}s")
    print(f"  FPS: {internal_params['fps']}")
    print(f"  Motion: {internal_params['motion_strength']}")
    print(f"  Style: {internal_params['visual_style']}")
    print(f"  Mood: {internal_params['mood']}")
    
    # Step 4: Create Director Intent for compilation
    print("\n4. Creating Director Intent...")
    
    camera_motion = CameraMotion(
        motion_type=CameraMotionType(internal_params['camera_motion']['type']),
        strength=MotionStrength(internal_params['camera_motion']['strength']),
        speed=internal_params['camera_motion']['speed'],
        easing=internal_params['camera_motion']['easing']
    )
    
    shot = Shot(
        shot_id="shot_001",
        scene_id="scene_001",
        prompt="Luxury watch on elegant marble display, soft lighting, premium materials",
        camera_motion=camera_motion,
        fps=internal_params['fps'],
        duration=internal_params['duration'],
        motion_strength=MotionStrength(internal_params['motion_strength'])
    )
    
    scene = Scene(
        scene_id="scene_001",
        description="Product showcase scene",
        shots=[shot],
        scene_fps=internal_params['fps']
    )
    
    intent = DirectorIntent(
        intent_id="commercial_001",
        narrative_description="Luxury product commercial",
        visual_theme=internal_params['visual_style'],
        mood=internal_params['mood'],
        target_providers=['runway', 'pika'],
        scenes=[scene]
    )
    
    # Step 5: Compile to model-specific prompts
    print("5. Compiling for video generation models...")
    compiler = PromptCompiler()
    result = compiler.compile(intent)
    
    print(f"\nCompilation Complete:")
    print(f"  Models: {len(result.model_prompts)} providers")
    print(f"  Shots: {len(result.shot_list)}")
    print(f"  Compilation time: {result.compilation_time:.3f}s")
    
    # Step 6: Show model-specific prompts
    print("\n6. Model-Specific Prompts:")
    for model_prompt in result.model_prompts:
        print(f"\n  Provider: {model_prompt.provider.upper()}")
        print(f"  Prompt: {model_prompt.compiled_prompt[:80]}...")
        print(f"  Parameters:")
        for key, value in model_prompt.control_parameters.items():
            print(f"    {key}: {value}")
    
    print("\n✅ Ready for video generation!\n")


def example_2_iterative_refinement():
    """Example 2: Iterative refinement workflow"""
    print("=" * 70)
    print("EXAMPLE 2: Iterative Refinement Workflow")
    print("=" * 70)
    
    # Step 1: Start with Drama preset
    print("\n1. Starting with Drama preset...")
    controls = PresetLibrary.get_preset(StylePreset.DRAMA)
    controls.timing.duration = 6.0
    
    # Step 2: Generate first version
    print("2. Generating first version...")
    v1_params = controls.to_internal_params()
    print(f"   Camera speed: {v1_params['camera_motion']['speed']}")
    print(f"   Motion strength: {v1_params['motion_strength']}")
    
    # Simulate generation result
    comp1 = GenerationComparison(
        generation_id="gen_001",
        parameters=v1_params,
        rating=3,
        notes="Camera too slow, lacks energy"
    )
    controls.add_comparison(comp1)
    
    # Step 3: Lock good parameters
    print("\n3. Locking successful parameters...")
    controls.lock_parameter("camera.shot_type", ShotType.CLOSEUP.value, "Perfect framing")
    controls.lock_parameter("camera.focal_length", 85, "85mm bokeh is ideal")
    controls.lock_parameter("timing.duration", 6.0, "6s is perfect length")
    print(f"   Locked: {len(controls.locked_parameters)} parameters")
    
    # Step 4: Create variation
    print("\n4. Creating variation with increased speed...")
    workflow = IterationWorkflow(controls)
    variation = workflow.create_variation({
        "camera.speed": 0.7,
        "motion.overall_strength": MotionStrengthLevel.MODERATE.value
    })
    
    v2_params = variation.to_internal_params()
    print(f"   New camera speed: {v2_params['camera_motion']['speed']}")
    print(f"   New motion strength: {v2_params['motion_strength']}")
    print(f"   Locked focal length preserved: {v2_params['focal_length']}mm")
    
    # Simulate second generation
    comp2 = GenerationComparison(
        generation_id="gen_002",
        parameters=v2_params,
        rating=5,
        notes="Perfect! Great balance of motion and clarity"
    )
    variation.add_comparison(comp2)
    
    # Step 5: Compare results
    print("\n5. Comparing generations...")
    comparison_data = workflow.compare_generations([comp1, comp2])
    print(f"   Total generations: {comparison_data['total_generations']}")
    print(f"   Best generation: {comparison_data['best_generation']}")
    print(f"   Average rating: {comparison_data['average_rating']:.1f}")
    
    # Step 6: Use best for production
    print("\n6. Selecting best for production...")
    best = variation.get_best_generation()
    print(f"   Selected: {best.generation_id}")
    print(f"   Rating: {best.rating}/5 stars")
    print(f"   Notes: {best.notes}")
    
    print("\n✅ Final configuration ready!\n")


def example_3_auto_mode_workflow():
    """Example 3: Auto mode for casual users"""
    print("=" * 70)
    print("EXAMPLE 3: Auto Mode for Casual Users")
    print("=" * 70)
    
    # Step 1: Simple inputs
    print("\n1. User provides simple inputs...")
    content_type = "product"
    mood = "exciting"
    duration = 5.0
    
    print(f"   Content Type: {content_type}")
    print(f"   Mood: {mood}")
    print(f"   Duration: {duration}s")
    
    # Step 2: Auto assistant suggests controls
    print("\n2. Auto assistant suggests controls...")
    controls = AutoModeAssistant.suggest_controls(
        content_type=content_type,
        mood=mood,
        duration=duration
    )
    
    print(f"   Mode: {controls.mode}")
    print(f"   Applied preset: {controls.style_preset}")
    print(f"   Camera movement: {controls.camera.movement_type.value}")
    print(f"   Camera speed: {controls.camera.speed}")
    print(f"   Motion strength: {controls.motion.overall_strength.value}")
    
    # Step 3: Generate immediately
    print("\n3. Converting to generation parameters...")
    params = controls.to_internal_params()
    
    print(f"   Ready parameters:")
    print(f"     - Camera: {params['camera_motion']['type']}")
    print(f"     - Shot: {params['shot_type']}")
    print(f"     - FPS: {params['fps']}")
    print(f"     - Duration: {params['duration']}s")
    
    # Optional Step 4: Upgrade to Pro mode
    print("\n4. (Optional) Upgrading to Pro mode for fine-tuning...")
    controls.mode = DirectorMode.PRO
    controls.depth_of_field = 0.3
    controls.camera.focal_length = 50
    
    print(f"   Now in Pro mode")
    print(f"   Added DOF control: {controls.depth_of_field}")
    print(f"   Set focal length: {controls.camera.focal_length}mm")
    
    print("\n✅ Video ready to generate!\n")


def example_4_multi_shot_sequence():
    """Example 4: Multi-shot sequence with different presets"""
    print("=" * 70)
    print("EXAMPLE 4: Multi-Shot Sequence")
    print("=" * 70)
    
    # Define shots with different styles
    shot_configs = [
        {
            "name": "Establishing Shot",
            "preset": StylePreset.ART_HOUSE,
            "duration": 4.0,
            "prompt": "Wide shot of city skyline at golden hour"
        },
        {
            "name": "Product Introduction",
            "preset": StylePreset.COMMERCIAL,
            "duration": 6.0,
            "prompt": "Elegant product reveal on minimalist background"
        },
        {
            "name": "Detail Shot",
            "preset": StylePreset.DRAMA,
            "duration": 5.0,
            "prompt": "Extreme closeup of product details and craftsmanship"
        },
        {
            "name": "Lifestyle Shot",
            "preset": StylePreset.COMMERCIAL,
            "duration": 5.0,
            "prompt": "Product in use, dynamic lifestyle context"
        }
    ]
    
    print(f"\n1. Creating {len(shot_configs)} shots...")
    
    shots = []
    scenes = []
    
    for i, config in enumerate(shot_configs, 1):
        print(f"\n   Shot {i}: {config['name']}")
        print(f"     Preset: {config['preset'].value}")
        
        # Load preset
        controls = PresetLibrary.get_preset(config['preset'])
        controls.timing.duration = config['duration']
        
        # Convert to internal params
        internal_params = controls.to_internal_params()
        
        # Create camera motion
        camera_motion = CameraMotion(
            motion_type=CameraMotionType(internal_params['camera_motion']['type']),
            strength=MotionStrength(internal_params['camera_motion']['strength']),
            speed=internal_params['camera_motion']['speed']
        )
        
        # Create shot
        shot = Shot(
            shot_id=f"shot_{i:03d}",
            scene_id="scene_001",
            prompt=config['prompt'],
            camera_motion=camera_motion,
            fps=internal_params['fps'],
            duration=internal_params['duration'],
            motion_strength=MotionStrength(internal_params['motion_strength'])
        )
        
        shots.append(shot)
        print(f"     Duration: {shot.duration}s @ {shot.fps}fps")
        print(f"     Camera: {camera_motion.motion_type.value}")
    
    # Step 2: Create scene
    print("\n2. Creating multi-shot scene...")
    scene = Scene(
        scene_id="scene_001",
        description="Product commercial sequence",
        shots=shots,
        scene_fps=30,
        total_duration=sum(s.duration for s in shots)
    )
    
    print(f"   Total shots: {len(scene.shots)}")
    print(f"   Total duration: {scene.total_duration}s")
    
    # Step 3: Create intent
    print("\n3. Creating director intent...")
    intent = DirectorIntent(
        intent_id="sequence_001",
        narrative_description="Multi-shot product commercial",
        visual_theme="cinematic_premium",
        mood="aspirational",
        target_providers=['runway', 'pika', 'sora'],
        scenes=[scene]
    )
    
    # Step 4: Compile
    print("\n4. Compiling for multiple providers...")
    compiler = PromptCompiler()
    result = compiler.compile(intent)
    
    print(f"   Compiled {len(result.model_prompts)} model versions")
    print(f"   Total shots: {len(result.shot_list)}")
    print(f"   Providers: {[p.provider for p in result.model_prompts]}")
    
    # Step 5: Show breakdown
    print("\n5. Shot breakdown:")
    for i, shot in enumerate(result.shot_list, 1):
        print(f"   Shot {i}:")
        print(f"     ID: {shot.shot_id}")
        print(f"     Duration: {shot.duration}s")
        print(f"     FPS: {shot.fps}")
        print(f"     Camera: {shot.camera_motion.motion_type.value if shot.camera_motion else 'N/A'}")
    
    print("\n✅ Multi-shot sequence ready for generation!\n")


def example_5_with_determinism():
    """Example 5: Using determinism for reproducible results"""
    print("=" * 70)
    print("EXAMPLE 5: Deterministic Generation")
    print("=" * 70)
    
    # Step 1: Create controls with seed
    print("\n1. Setting up deterministic generation...")
    controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
    
    # Step 2: Convert to internal params
    internal_params = controls.to_internal_params()
    
    # Step 3: Create shot with determinism config
    print("\n2. Creating shot with fixed seed...")
    determinism = DeterminismConfig(
        seed=42,
        use_fixed_seed=True,
        reproducibility_level="standard"
    )
    
    camera_motion = CameraMotion(
        motion_type=CameraMotionType(internal_params['camera_motion']['type']),
        strength=MotionStrength(internal_params['camera_motion']['strength']),
        speed=internal_params['camera_motion']['speed']
    )
    
    shot = Shot(
        shot_id="shot_001",
        scene_id="scene_001",
        prompt="Product showcase with consistent results",
        camera_motion=camera_motion,
        fps=internal_params['fps'],
        duration=internal_params['duration'],
        determinism=determinism
    )
    
    print(f"   Seed: {determinism.seed}")
    print(f"   Fixed seed: {determinism.use_fixed_seed}")
    
    # Step 4: Create intent with global determinism
    print("\n3. Creating intent with global determinism...")
    scene = Scene(scene_id="scene_001", shots=[shot])
    
    intent = DirectorIntent(
        intent_id="deterministic_001",
        narrative_description="Reproducible generation",
        target_providers=['runway', 'pika'],
        scenes=[scene],
        global_determinism=determinism
    )
    
    # Step 5: Compile
    print("\n4. Compiling with seed management...")
    compiler = PromptCompiler()
    result = compiler.compile(intent)
    
    print(f"   Seed manifest: {result.seed_manifest}")
    print(f"   Model prompts: {len(result.model_prompts)}")
    
    # Show seed in parameters
    print("\n5. Seeds in model parameters:")
    for model_prompt in result.model_prompts:
        if 'seed' in model_prompt.control_parameters:
            print(f"   {model_prompt.provider}: seed={model_prompt.control_parameters['seed']}")
    
    print("\n✅ Deterministic generation configured!\n")


def main():
    """Run all integration examples"""
    examples = [
        ("Simple Commercial", example_1_simple_commercial),
        ("Iterative Refinement", example_2_iterative_refinement),
        ("Auto Mode Workflow", example_3_auto_mode_workflow),
        ("Multi-Shot Sequence", example_4_multi_shot_sequence),
        ("Deterministic Generation", example_5_with_determinism)
    ]
    
    print("\n" + "=" * 70)
    print("DIRECTOR UX - FULL INTEGRATION EXAMPLES")
    print("=" * 70)
    print("\nThis demo shows complete integration of Director UX with ANIMAtiZE:")
    print("  - UX Controls → Internal Parameters")
    print("  - Internal Parameters → Director Intent")
    print("  - Director Intent → Model-Specific Prompts")
    print("  - Ready for Video Generation APIs")
    print("\n" + "=" * 70)
    
    for i, (name, example_func) in enumerate(examples, 1):
        print(f"\n\n[{i}/{len(examples)}] {name.upper()}")
        try:
            example_func()
            if i < len(examples):
                input("\nPress Enter to continue to next example...")
        except KeyboardInterrupt:
            print("\n\nExamples interrupted by user.")
            break
        except Exception as e:
            print(f"\nError in example: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nThe Director UX Control Surface is fully integrated and ready for use!")
    print("\nNext steps:")
    print("  1. Implement UI based on wireframes in DIRECTOR_UX_SPECIFICATION.md")
    print("  2. Connect to actual video generation APIs")
    print("  3. Add real-time preview capabilities")
    print("  4. Build comparison visualization interface")
    print("\n")


if __name__ == "__main__":
    main()

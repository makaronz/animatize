"""
Director UX Control Surface - Usage Examples

Demonstrates various workflows and use cases for the Director UX system.
"""

import json
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
    GenerationComparison
)


def example_1_pro_mode_basic():
    """Example 1: Basic Pro Mode setup"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Pro Mode Setup")
    print("=" * 60)
    
    # Create controls in Pro mode
    controls = DirectorControls(mode=DirectorMode.PRO)
    
    # Configure camera
    controls.camera.movement_type = CameraMovementType.DOLLY
    controls.camera.shot_type = ShotType.CLOSEUP
    controls.camera.angle = CameraAngle.EYE_LEVEL
    controls.camera.focal_length = 85
    controls.camera.speed = 0.8
    controls.camera.strength = MotionStrengthLevel.MODERATE
    controls.camera.easing = "ease_in_out"
    
    # Configure timing
    controls.timing.duration = 7.0
    controls.timing.fps = 30
    
    # Configure motion
    controls.motion.overall_strength = MotionStrengthLevel.SUBTLE
    controls.motion.subject_motion = 0.3
    controls.motion.camera_motion = 0.7
    
    # Set style
    controls.visual_style = "cinematic"
    controls.mood = "intimate"
    controls.color_grade = "warm"
    
    print(f"Control ID: {controls.control_id}")
    print(f"Mode: {controls.mode}")
    print(f"\nCamera Settings:")
    print(f"  Movement: {controls.camera.movement_type.value}")
    print(f"  Shot Type: {controls.camera.shot_type.value}")
    print(f"  Speed: {controls.camera.speed}")
    print(f"\nTiming:")
    print(f"  Duration: {controls.timing.duration}s")
    print(f"  FPS: {controls.timing.fps}")
    print(f"\nInternal Parameters:")
    print(json.dumps(controls.to_internal_params(), indent=2))
    print()


def example_2_preset_usage():
    """Example 2: Using style presets"""
    print("=" * 60)
    print("EXAMPLE 2: Using Style Presets")
    print("=" * 60)
    
    # List available presets
    print("\nAvailable Presets:")
    for preset in PresetLibrary.list_presets():
        print(f"\n{preset['name'].upper()}")
        print(f"  Description: {preset['description']}")
        print(f"  Use Case: {preset['use_case']}")
    
    # Load commercial preset
    print("\n" + "-" * 60)
    print("Loading COMMERCIAL preset...")
    print("-" * 60)
    
    commercial = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
    
    print(f"\nPreset: {commercial.style_preset}")
    print(f"Camera: {commercial.camera.movement_type.value}")
    print(f"  Shot: {commercial.camera.shot_type.value}")
    print(f"  Speed: {commercial.camera.speed}")
    print(f"  Focal Length: {commercial.camera.focal_length}mm")
    print(f"Timing: {commercial.timing.duration}s @ {commercial.timing.fps}fps")
    print(f"Motion: {commercial.motion.overall_strength.value}")
    print(f"Style: {commercial.visual_style}")
    print(f"Mood: {commercial.mood}")
    print(f"Color Grade: {commercial.color_grade}")
    
    # Customize the preset
    print("\nCustomizing preset...")
    commercial.timing.duration = 8.0
    commercial.mood = "luxury"
    
    print(f"Modified Duration: {commercial.timing.duration}s")
    print(f"Modified Mood: {commercial.mood}")
    print()


def example_3_parameter_locking():
    """Example 3: Parameter locking for iteration"""
    print("=" * 60)
    print("EXAMPLE 3: Parameter Locking and Iteration")
    print("=" * 60)
    
    # Start with a preset
    controls = PresetLibrary.get_preset(StylePreset.ACTION)
    
    print("Starting with ACTION preset")
    print(f"Initial camera speed: {controls.camera.speed}")
    print(f"Initial motion strength: {controls.motion.overall_strength.value}")
    
    # Lock good parameters
    print("\nLocking parameters that work well...")
    controls.lock_parameter(
        "camera.movement_type",
        CameraMovementType.HANDHELD.value,
        "Handheld gives perfect energy for action"
    )
    controls.lock_parameter(
        "timing.fps",
        60,
        "60fps allows for great slow-mo options"
    )
    
    print("Locked parameters:")
    for param_name, lock in controls.locked_parameters.items():
        print(f"  {param_name}: {lock.locked_value}")
        print(f"    Notes: {lock.notes}")
    
    # Create variation
    print("\nCreating variation with modified speed...")
    workflow = IterationWorkflow(controls)
    
    variation = workflow.create_variation({
        "camera.speed": 2.0,  # Increase speed
        "motion.overall_strength": MotionStrengthLevel.EXTREME.value
    })
    
    print(f"\nOriginal speed: {controls.camera.speed}")
    print(f"Variation speed: {variation.camera.speed}")
    print(f"\nOriginal motion: {controls.motion.overall_strength.value}")
    print(f"Variation motion: {variation.motion.overall_strength.value}")
    print(f"\nLocked FPS preserved: {variation.timing.fps}")
    print()


def example_4_generation_comparison():
    """Example 4: Comparing multiple generations"""
    print("=" * 60)
    print("EXAMPLE 4: Generation Comparison")
    print("=" * 60)
    
    controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
    
    # Simulate 3 generations
    comparisons = [
        GenerationComparison(
            generation_id="gen_001",
            parameters={"camera.speed": 0.6, "motion.strength": "subtle"},
            result_url="https://example.com/video_001.mp4",
            thumbnail_url="https://example.com/thumb_001.jpg",
            rating=3,
            notes="Too slow, feels sluggish"
        ),
        GenerationComparison(
            generation_id="gen_002",
            parameters={"camera.speed": 0.8, "motion.strength": "moderate"},
            result_url="https://example.com/video_002.mp4",
            thumbnail_url="https://example.com/thumb_002.jpg",
            rating=5,
            notes="Perfect! Smooth and professional"
        ),
        GenerationComparison(
            generation_id="gen_003",
            parameters={"camera.speed": 1.2, "motion.strength": "strong"},
            result_url="https://example.com/video_003.mp4",
            thumbnail_url="https://example.com/thumb_003.jpg",
            rating=2,
            notes="Too fast, creates motion sickness"
        )
    ]
    
    # Add to controls
    for comp in comparisons:
        controls.add_comparison(comp)
    
    print(f"Total generations: {len(controls.generation_history)}")
    
    # Get best
    best = controls.get_best_generation()
    print(f"\nBest generation: {best.generation_id}")
    print(f"  Rating: {best.rating} stars")
    print(f"  Parameters: {json.dumps(best.parameters, indent=2)}")
    print(f"  Notes: {best.notes}")
    
    # Compare all
    workflow = IterationWorkflow(controls)
    comparison_data = workflow.compare_generations(controls.generation_history)
    
    print(f"\nComparison Analysis:")
    print(f"  Total: {comparison_data['total_generations']}")
    print(f"  Rated: {comparison_data['rated_count']}")
    print(f"  Average rating: {comparison_data.get('average_rating', 'N/A'):.1f}")
    print(f"  Best: {comparison_data.get('best_generation', 'N/A')}")
    print()


def example_5_refinement_suggestions():
    """Example 5: AI-powered refinement suggestions"""
    print("=" * 60)
    print("EXAMPLE 5: Refinement Suggestions")
    print("=" * 60)
    
    controls = DirectorControls(mode=DirectorMode.PRO)
    controls.camera.speed = 1.8
    controls.timing.duration = 3.0
    controls.motion.overall_strength = MotionStrengthLevel.EXTREME
    
    print("Current settings:")
    print(f"  Camera speed: {controls.camera.speed}")
    print(f"  Duration: {controls.timing.duration}s")
    print(f"  Motion: {controls.motion.overall_strength.value}")
    
    # Get suggestions based on feedback
    workflow = IterationWorkflow(controls)
    
    feedback_scenarios = [
        "Camera moves too fast and feels rushed",
        "Too chaotic and unstable",
        "Scene is too short, I can't see what's happening"
    ]
    
    for feedback in feedback_scenarios:
        print(f"\nFeedback: \"{feedback}\"")
        suggestions = workflow.suggest_refinements(controls, feedback)
        
        if suggestions:
            print("Suggestions:")
            for sug in suggestions:
                print(f"  Parameter: {sug['parameter']}")
                print(f"    Current: {sug['current_value']}")
                print(f"    Suggested: {sug['suggested_value']}")
                print(f"    Reason: {sug['reason']}")
        else:
            print("  No specific suggestions")
    print()


def example_6_auto_mode():
    """Example 6: Auto mode for quick setup"""
    print("=" * 60)
    print("EXAMPLE 6: Auto Mode Quick Setup")
    print("=" * 60)
    
    # Show available options
    options = AutoModeAssistant.get_quick_options()
    
    print("Available Quick Options:")
    print(f"\nContent Types: {', '.join(options['content_types'])}")
    print(f"Moods: {', '.join(options['moods'])}")
    print(f"Durations: {', '.join(options['durations'])}")
    
    # Create controls for different scenarios
    scenarios = [
        ("product", "exciting", 5.0),
        ("interview", "calm", 8.0),
        ("artistic", "mysterious", 12.0),
        ("sport", "energetic", 3.0)
    ]
    
    for content_type, mood, duration in scenarios:
        print("\n" + "-" * 60)
        print(f"Auto Mode: {content_type.upper()} / {mood} / {duration}s")
        print("-" * 60)
        
        controls = AutoModeAssistant.suggest_controls(
            content_type=content_type,
            mood=mood,
            duration=duration
        )
        
        print(f"Mode: {controls.mode}")
        print(f"Preset: {controls.style_preset}")
        print(f"Camera: {controls.camera.movement_type.value}")
        print(f"  Shot: {controls.camera.shot_type.value}")
        print(f"  Speed: {controls.camera.speed}")
        print(f"Motion: {controls.motion.overall_strength.value}")
        print(f"Mood: {controls.mood}")
    print()


def example_7_full_workflow():
    """Example 7: Complete professional workflow"""
    print("=" * 60)
    print("EXAMPLE 7: Complete Professional Workflow")
    print("=" * 60)
    
    # Step 1: Start with preset
    print("\nStep 1: Load base preset")
    controls = PresetLibrary.get_preset(StylePreset.DRAMA)
    print(f"  Loaded: {controls.style_preset}")
    
    # Step 2: Customize
    print("\nStep 2: Customize for specific scene")
    controls.camera.focal_length = 85
    controls.timing.duration = 6.0
    controls.mood = "tense"
    controls.color_grade = "cool"
    print(f"  Focal length: {controls.camera.focal_length}mm")
    print(f"  Duration: {controls.timing.duration}s")
    print(f"  Mood: {controls.mood}")
    
    # Step 3: First generation
    print("\nStep 3: Generate first version")
    params_v1 = controls.to_internal_params()
    print(f"  Generated with params: {len(params_v1)} parameters")
    
    # Step 4: Review and lock good parameters
    print("\nStep 4: Review and lock successful parameters")
    controls.lock_parameter(
        "camera.focal_length",
        85,
        "85mm perfect for close emotional shots"
    )
    controls.lock_parameter(
        "timing.duration",
        6.0,
        "6 seconds gives right pacing"
    )
    print(f"  Locked: {len(controls.locked_parameters)} parameters")
    
    # Step 5: Create variations
    print("\nStep 5: Create variations")
    workflow = IterationWorkflow(controls)
    
    variations = [
        {"camera.speed": 0.3, "motion.overall_strength": "subtle"},
        {"camera.speed": 0.5, "motion.overall_strength": "moderate"},
        {"camera.speed": 0.7, "motion.overall_strength": "moderate"}
    ]
    
    for i, changes in enumerate(variations, 1):
        variation = workflow.create_variation(changes)
        print(f"  Variation {i}: speed={changes['camera.speed']}, "
              f"motion={changes['motion.overall_strength']}")
        
        # Simulate adding comparison
        comp = GenerationComparison(
            generation_id=f"gen_{i:03d}",
            parameters=changes,
            rating=3 + (i % 3),  # Simulate ratings
            notes=f"Variation {i} test"
        )
        controls.add_comparison(comp)
    
    # Step 6: Select best
    print("\nStep 6: Select best generation")
    best = controls.get_best_generation()
    print(f"  Best: {best.generation_id} ({best.rating} stars)")
    print(f"  Parameters: {json.dumps(best.parameters, indent=2)}")
    
    # Step 7: Export final configuration
    print("\nStep 7: Export final configuration")
    final_config = controls.to_dict()
    print(f"  Exported {len(final_config)} configuration fields")
    print(f"  Ready for production generation")
    print()


def example_8_batch_preset_comparison():
    """Example 8: Compare all presets for same content"""
    print("=" * 60)
    print("EXAMPLE 8: Batch Preset Comparison")
    print("=" * 60)
    
    presets_to_compare = [
        StylePreset.DOCUMENTARY,
        StylePreset.COMMERCIAL,
        StylePreset.ART_HOUSE,
        StylePreset.ACTION,
        StylePreset.DRAMA
    ]
    
    print("\nComparing presets for product showcase:\n")
    
    comparison_table = []
    
    for preset in presets_to_compare:
        controls = PresetLibrary.get_preset(preset)
        
        comparison_table.append({
            "Preset": preset.value,
            "Camera": controls.camera.movement_type.value,
            "Shot": controls.camera.shot_type.value,
            "Speed": controls.camera.speed,
            "Motion": controls.motion.overall_strength.value,
            "FPS": controls.timing.fps,
            "Duration": f"{controls.timing.duration}s"
        })
    
    # Print comparison table
    headers = ["Preset", "Camera", "Shot", "Speed", "Motion", "FPS", "Duration"]
    
    print(f"{'Preset':<15} {'Camera':<12} {'Shot':<12} {'Speed':<6} "
          f"{'Motion':<10} {'FPS':<5} {'Duration'}")
    print("-" * 80)
    
    for row in comparison_table:
        print(f"{row['Preset']:<15} {row['Camera']:<12} {row['Shot']:<12} "
              f"{row['Speed']:<6.1f} {row['Motion']:<10} {row['FPS']:<5} "
              f"{row['Duration']}")
    
    print("\nRecommendation: COMMERCIAL preset best suited for product showcase")
    print("  - Moderate speed (0.6) for clear product view")
    print("  - Dolly movement for professional feel")
    print("  - 30fps for smooth playback")
    print()


def example_9_transition_setup():
    """Example 9: Setting up transitions between shots"""
    print("=" * 60)
    print("EXAMPLE 9: Transition Setup")
    print("=" * 60)
    
    # Create two shots with different transitions
    shot_configs = [
        {
            "name": "Opening Shot",
            "preset": StylePreset.ART_HOUSE,
            "transition": TransitionControl(
                style=TransitionStyle.FADE_FROM_BLACK,
                duration=2.0
            )
        },
        {
            "name": "Main Shot",
            "preset": StylePreset.DRAMA,
            "transition": TransitionControl(
                style=TransitionStyle.DISSOLVE,
                duration=1.5
            )
        },
        {
            "name": "Closing Shot",
            "preset": StylePreset.ART_HOUSE,
            "transition": TransitionControl(
                style=TransitionStyle.FADE_TO_BLACK,
                duration=2.0
            )
        }
    ]
    
    print("\nShot sequence with transitions:\n")
    
    for i, config in enumerate(shot_configs, 1):
        controls = PresetLibrary.get_preset(config["preset"])
        controls.transition = config["transition"]
        
        print(f"Shot {i}: {config['name']}")
        print(f"  Style: {config['preset'].value}")
        print(f"  Duration: {controls.timing.duration}s")
        print(f"  Transition: {controls.transition.style.value} "
              f"({controls.transition.duration}s)")
        if i < len(shot_configs):
            print("  ↓")
    
    print("\nTotal sequence length: ~", 
          sum(controls.timing.duration for _ in shot_configs), "seconds")
    print()


def main():
    """Run all examples"""
    examples = [
        example_1_pro_mode_basic,
        example_2_preset_usage,
        example_3_parameter_locking,
        example_4_generation_comparison,
        example_5_refinement_suggestions,
        example_6_auto_mode,
        example_7_full_workflow,
        example_8_batch_preset_comparison,
        example_9_transition_setup
    ]
    
    for example in examples:
        try:
            example()
            input("Press Enter to continue to next example...")
            print("\n\n")
        except KeyboardInterrupt:
            print("\n\nExamples interrupted by user.")
            break
        except Exception as e:
            print(f"\nError in example: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

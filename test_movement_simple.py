#!/usr/bin/env python3
"""
Simple test for Movement Predictor Module
"""

import sys
import os
sys.path.append(str(os.path.dirname(__file__)))

from src.analyzers.movement_predictor import MovementPredictor
import tempfile
import numpy as np
import cv2
import shutil

def test_movement_predictor():
    """Simple test of movement predictor functionality"""
    print("🎬 Testing Movement Predictor Module...")
    
    # Create test directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test images
        test_img = '139_2.jpg'
        
        # Initialize predictor
        predictor = MovementPredictor()
        print("✅ Movement Predictor initialized")
        
        # Test image analysis
        analysis = predictor.analyze_image(test_img)
        print("✅ Image analysis completed")
        
        # Check results
        if 'error' not in analysis:
            predictions = analysis['movement_predictions']
            
            # Character actions
            char_actions = predictions['character_actions']
            print(f"✅ Character actions detected: {len(char_actions)}")
            for action in char_actions:
                print(f"   - {action['predicted_action']} ({action['justification']})")
            
            # Camera movements
            cam_moves = predictions['camera_movements']
            print(f"✅ Camera movements predicted: {len(cam_moves)}")
            for move in cam_moves:
                print(f"   - {move['type']} {move['direction']} ({move['justification']})")
            
            # Environmental animations
            env_moves = predictions['environment_animations']
            print(f"✅ Environmental animations: {len(env_moves)}")
            for move in env_moves:
                print(f"   - {move['element']} {move['motion']} ({move['justification']})")
            
            # Generate cinematic prompt
            cinematic_prompt = predictor.get_cinematic_movement_prompt(test_img)
            print("\n🎥 Cinematic Movement Prompt:")
            print(f"   {cinematic_prompt}")
            
            # Save analysis
            output_path = os.path.join(temp_dir, 'analysis.json')
            predictor.save_analysis(analysis, output_path)
            print(f"✅ Analysis saved to {output_path}")
            
            return True
        else:
            print(f"❌ Error: {analysis['error']}")
            return False
            
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    success = test_movement_predictor()
    if success:
        print("\n🎉 Movement Predictor Module test PASSED!")
    else:
        print("\n💥 Movement Predictor Module test FAILED!")
        sys.exit(1)
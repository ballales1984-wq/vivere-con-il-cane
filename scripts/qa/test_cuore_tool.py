#!/usr/bin/env python
"""
Test script for heart sound analysis tool.
Tests analyze_heart_sound() function directly.
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from canine_tools.views import analyze_heart_sound

def test_heart_analysis():
    """Test the heart sound analysis with the available WAV file."""
    
    # Check available WAV files
    wav_files = [f for f in os.listdir('.') if f.endswith('.wav')]
    print(f"Found WAV files: {wav_files}")
    
    if not wav_files:
        print("No WAV files found!")
        return
    
    test_file = wav_files[0]
    print(f"\nTesting with: {test_file}")
    print("=" * 60)
    
    try:
        # Run analysis
        result = analyze_heart_sound(test_file, context="Test diretto da script")
        
        print("\n*** ANALYSIS SUCCESSFUL! ***\n")
        
        print(f"Duration: {result.get('duration', 'N/A'):.2f} seconds")
        print(f"BPM: {result.get('bpm', 0)}")
        print(f"Beat Count: {result.get('beat_count', 0)}")
        print(f"Confidence: {result.get('confidence', 0)}")
        print(f"Sample Rate: {result.get('sample_rate', 'N/A')}")
        
        s1_s2 = result.get('s1_s2')
        if s1_s2:
            print(f"\nS1/S2 Detection:")
            print(f"  S1 count: {s1_s2.get('s1_count', 0)}")
            print(f"  S2 count: {s1_s2.get('s2_count', 0)}")
            print(f"  S1 avg amplitude: {s1_s2.get('s1_avg_amplitude', 0):.4f}")
            print(f"  S2 avg amplitude: {s1_s2.get('s2_avg_amplitude', 0):.4f}")
        
        hrv = result.get('hrv')
        if hrv:
            print(f"\nHRV Metrics:")
            print(f"  SDNN: {hrv.get('sdnn_sec', 0):.4f}s")
            print(f"  RMSSD: {hrv.get('rmssd_sec', 0):.4f}s")
            print(f"  pNN50: {hrv.get('pnn50_percent', 0):.1f}%")
        
        print(f"\nPeak count: {len(result.get('peak_times', []))}")
        print(f"First 5 peaks (seconds): {[f'{t:.2f}' for t in result.get('peak_times', [])[:5]]}")
        
        print("\n" + "=" * 60)
        print("OK - Tool cuore FUNZIONA!")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] ANALYSIS FAILED!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_heart_analysis()

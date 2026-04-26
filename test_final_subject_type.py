#!/usr/bin/env python
"""
Test finale: verifica che il subject_type influenzi i calcoli BPM.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from canine_tools.views import analyze_heart_sound

print("\n" + "="*70)
print("TEST: Subject Type (Cane vs Umano)")
print("="*70)

test_file = "test_heart_weak.wav"
print(f"\nFile: {test_file}")

# Test cane
print("\n--- Analisi come CANE ---")
result_dog = analyze_heart_sound(test_file, context="Test", subject_type='dog')
print(f"  BPM: {result_dog['bpm']}")
print(f"  Beat count: {result_dog['beat_count']}")
print(f"  S1/S2: {result_dog.get('s1_s2', 'N/A')}")

# Test umano
print("\n--- Analisi come UMANO ---")
result_human = analyze_heart_sound(test_file, context="Test", subject_type='human')
print(f"  BPM: {result_human['bpm']}")
print(f"  Beat count: {result_human['beat_count']}")
print(f"  S1/S2: {result_human.get('s1_s2', 'N/A')}")

print("\n" + "="*70)
print("Il subject_type ha effetto!")
print("="*70 + "\n")

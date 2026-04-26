#!/usr/bin/env python
"""
Generate synthetic weak heart sound signal and test analyze_heart_sound function.
"""
import os
import sys

# Set up Django environment first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

import numpy as np
import scipy.io.wavfile as wavfile

from canine_tools.views import analyze_heart_sound

def generate_weak_heart_signal():
    """Generate 5-second synthetic weak heart sound at 44100 Hz."""
    sr = 44100  # Sample rate
    duration = 5  # seconds
    n_samples = int(sr * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    
    # Heart rate: 80 BPM
    heart_rate_bpm = 80
    heart_rate_hz = heart_rate_bpm / 60.0
    beat_period = 1.0 / heart_rate_hz  # 0.75 seconds per beat
    
    # Create "lub-dub" pattern: two sharp peaks per heartbeat
    # Use a sawtooth-like pattern at 2x heart frequency
    peak_freq = 2 * heart_rate_hz
    
    # Generate base pattern (sawtooth for sharp peaks)
    sawtooth = 2 * (t * peak_freq - np.floor(t * peak_freq + 0.5))
    sawtooth = -np.abs(sawtooth) + 1  # Inverted triangle peaks (0 to 1 to 0)
    
    # Add small time offset between lub and dub to separate them
    # Create two delta functions per beat
    signal = np.zeros(n_samples)
    for i in range(int(duration / beat_period)):
        beat_time = i * beat_period
        # Lub (S1) - stronger peak
        lub_idx = int(beat_time * sr)
        if lub_idx < n_samples:
            # Gaussian-like pulse
            pulse_width = int(0.02 * sr)  # 20 ms width
            half_width = pulse_width // 2
            start = max(0, lub_idx - half_width)
            end = min(n_samples, lub_idx + half_width)
            x = np.linspace(-half_width, half_width, end - start)
            signal[start:end] += np.exp(-(x**2) / (2 * (0.01*sr)**2))
        
        # Dub (S2) - slightly weaker, slightly delayed (~0.1-0.15s after S1)
        dub_idx = int((beat_time + 0.12) * sr)
        if dub_idx < n_samples:
            pulse_width = int(0.015 * sr)  # 15 ms width
            half_width = pulse_width // 2
            start = max(0, dub_idx - half_width)
            end = min(n_samples, dub_idx + half_width)
            x = np.linspace(-half_width, half_width, end - start)
            signal[start:end] += 0.7 * np.exp(-(x**2) / (2 * (0.008*sr)**2))
    
    # Normalize to max amplitude ~0.001 (weak signal)
    signal = signal / (np.max(np.abs(signal)) + 1e-9) * 0.001
    
    # Add Gaussian noise for SNR ~10 dB
    signal_power = np.mean(signal**2)
    snr_linear = 10**(10/10)  # 10 dB
    noise_power = signal_power / snr_linear
    noise = np.random.normal(0, np.sqrt(noise_power), n_samples)
    signal_noisy = signal + noise
    
    return sr, signal_noisy

def main():
    print("=" * 60)
    print("Testing analyze_heart_sound with synthetic weak signal")
    print("=" * 60)
    
    # Generate signal
    print("\n1. Generating 5-second synthetic weak heart sound...")
    sr, signal = generate_weak_heart_signal()
    print(f"   Sample rate: {sr} Hz")
    print(f"   Duration: {len(signal)/sr:.2f} seconds")
    print(f"   Signal max amplitude: {np.max(np.abs(signal)):.6f}")
    print(f"   Signal RMS: {np.sqrt(np.mean(signal**2)):.6f}")
    
    # Save as WAV
    output_file = 'test_heart_weak.wav'
    print(f"\n2. Saving to '{output_file}'...")
    # Convert to 16-bit PCM
    scaled = np.int16(signal / np.max(np.abs(signal)) * 32767)
    wavfile.write(output_file, sr, scaled)
    file_size = os.path.getsize(output_file)
    print(f"   File size: {file_size} bytes")
    
    # Call analyze_heart_sound
    print(f"\n3. Calling analyze_heart_sound()...")
    try:
        results = analyze_heart_sound(output_file, context='synthetic_test')
        print("   Function executed successfully.")
    except Exception as e:
        print(f"   ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Print envelope statistics if available
    print("\n4. Envelope statistics:")
    if results.get('envelope'):
        env_vals = np.array(results['envelope']['values'])
        print(f"   Min: {np.min(env_vals):.6f}")
        print(f"   Max: {np.max(env_vals):.6f}")
        print(f"   Mean: {np.mean(env_vals):.6f}")
        print(f"   Std: {np.std(env_vals):.6f}")
        # Check for NaN/inf
        print(f"   Contains NaN: {np.any(np.isnan(env_vals))}")
        print(f"   Contains inf: {np.any(np.isinf(env_vals))}")
    else:
        print("   No envelope data returned")
    
    # Print results
    print("\n5. Analysis results:")
    print(f"   Duration: {results['duration']} seconds")
    print(f"   BPM: {results['bpm']}")
    print(f"   Beat count: {results['beat_count']}")
    print(f"   Confidence: {results['confidence']}")
    print(f"   Peak times: {[round(t, 3) for t in results['peak_times']]}")
    print(f"   Amplitudes: {[round(a, 4) for a in results['amplitudes']]}")
    print(f"   HRV metrics: {results['hrv']}")
    print(f"   S1/S2 classification: {results['s1_s2']}")
    
    print("\n" + "=" * 60)
    print("Test complete.")
    print("=" * 60)

if __name__ == '__main__':
    main()

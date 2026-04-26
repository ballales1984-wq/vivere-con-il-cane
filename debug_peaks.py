import numpy as np
import librosa
from scipy.signal import butter, filtfilt, hilbert, find_peaks, savgol_filter
import json

def bandpass_filter(signal, fs, low=20, high=150, order=4):
    nyq = fs / 2
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal)

# Carica
y, sr = librosa.load('test_heart_weak.wav', sr=None, mono=True, dtype=np.float32)
duration = len(y) / sr
y = y / (np.max(np.abs(y)) + 1e-9)

# Filtro
y_filt = bandpass_filter(y, sr)
if np.any(np.isnan(y_filt)) or np.any(np.isinf(y_filt)):
    y_filt = y

# Envelope
analytic = hilbert(y_filt)
envelope = np.abs(analytic)

max_window = 101
win_len = min(max_window, len(envelope) - 1 if len(envelope) % 2 == 0 else len(envelope))
if win_len > 3:
    if np.max(envelope) < 0.05:
        win_len = min(31, win_len)
    if win_len % 2 == 0:
        win_len = max(3, win_len - 1)
    envelope_smooth = savgol_filter(envelope, win_len, 3)
else:
    envelope_smooth = envelope

envelope_smooth = np.nan_to_num(envelope_smooth, nan=0.0, posinf=0.0, neginf=0.0)
env_min, env_max = np.min(envelope_smooth), np.max(envelope_smooth)
env_range = env_max - env_min
if env_range < 1e-6:
    abs_sig = np.abs(y_filt)
    max_abs = np.max(abs_sig)
    env_norm = abs_sig / (max_abs + 1e-9) if max_abs >= 1e-6 else np.zeros_like(envelope_smooth)
else:
    env_norm = (envelope_smooth - env_min) / (env_range + 1e-9)
env_norm = np.nan_to_num(env_norm, nan=0.0, posinf=0.0, neginf=0.0)
env_norm = np.clip(env_norm, 0.0, 1.0)

print(f"Sample rate: {sr} Hz")
print(f"Lunghezza segnale: {len(y)} campioni ({duration:.2f}s)")
print(f"Envelope min/max: {env_min:.4f} / {env_max:.4f}")
print(f"Envelope norm min/max: {np.min(env_norm):.4f} / {np.max(env_norm):.4f}")
print(f"Media envelope: {np.mean(env_norm):.4f}")
print(f"Dev.std envelope: {np.std(env_norm):.4f}")
print(f"Percentili: 50%={np.percentile(env_norm, 50):.4f}, 70%={np.percentile(env_norm, 70):.4f}, 80%={np.percentile(env_norm, 80):.4f}")

# Prova diverse threshold
thresholds = [0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12]
for th in thresholds:
    peaks, _ = find_peaks(env_norm, distance=int(0.2*sr), height=th, prominence=0.001)
    print(f"Threshold {th:.2f}: {len(peaks)} picchi")

# Prova prominence diverse
print("\nProminence test (th=0.08):")
for prom in [0.001, 0.002, 0.003, 0.005, 0.01]:
    peaks, _ = find_peaks(env_norm, distance=int(0.2*sr), height=0.08, prominence=prom)
    print(f"  Prominence {prom:.3f}: {len(peaks)} picchi")

# Prova distance diverse
print("\nDistance test (th=0.08, prom=0.001):")
for dist_factor in [0.15, 0.2, 0.25, 0.3, 0.35]:
    dist = int(dist_factor * sr)
    peaks, _ = find_peaks(env_norm, distance=dist, height=0.08, prominence=0.001)
    print(f"  Min distance {dist_factor*1000:.0f}ms ({dist} campioni): {len(peaks)} picchi")

# Salva envelope per ispezione
data = {
    'times': (np.arange(len(env_norm)) / sr).tolist(),
    'envelope': env_norm.tolist(),
    'sample_rate': sr
}
with open('envelope_debug.json', 'w') as f:
    json.dump(data, f)
print("\nEnvelope salvato in envelope_debug.json")

import numpy as np
import librosa
from scipy.signal import butter, filtfilt, hilbert, find_peaks, savgol_filter

def bandpass_filter(signal, fs, low=20, high=150, order=4):
    nyq = fs / 2
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal)

y, sr = librosa.load('test_heart_weak.wav', sr=None, mono=True, dtype=np.float32)
y = y / (np.max(np.abs(y)) + 1e-9)
y_filt = bandpass_filter(y, sr)
if np.any(np.isnan(y_filt)) or np.any(np.isinf(y_filt)):
    y_filt = y
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

# Detection permissiva
threshold_low = 0.05
min_distance_initial = int(0.15 * sr)
peaks_initial, _ = find_peaks(env_norm, distance=min_distance_initial, height=threshold_low, prominence=0.0005)

print(f"Picchi iniziali (permessivi): {len(peaks_initial)}")
peak_times_i = peaks_initial / sr
intervals_i = np.diff(peak_times_i)
print(f"  Intervalli: {[round(x,3) for x in intervals_i]}")

# threshold principale dinamica
if len(peaks_initial) >= 5:
    initial_amplitudes = env_norm[peaks_initial]
    median_amp = np.median(initial_amplitudes)
    mad = np.median(np.abs(initial_amplitudes - median_amp))
    threshold_main = median_amp + 1.5 * mad
    threshold_main = np.clip(threshold_main, 0.10, 0.80)
else:
    threshold_main = 0.10

print(f"Threshold main: {threshold_main:.4f}")

# min_distance adattivo
if len(peaks_initial) >= 3:
    median_interval = np.median(intervals_i)
    min_distance = max(int(0.30 * median_interval * sr), int(0.15 * sr))
else:
    min_distance = int(0.25 * sr)
print(f"Min distance: {min_distance} campioni ({min_distance/sr:.3f}s)")

# Prominence
peak_to_peak_var = np.std(env_norm[peaks_initial]) if len(peaks_initial) >= 3 else 0.03
prom = max(0.0005, 0.04 * threshold_main + 0.2 * peak_to_peak_var)
prom = min(prom, threshold_main * 0.4)
print(f"Prominence: {prom:.4f}")

# Rilevazione principale
peaks, props = find_peaks(env_norm, distance=min_distance, height=threshold_main, prominence=prom)
print(f"\nPicchi principali: {len(peaks)}")
peak_times = peaks / sr
if len(peaks) > 0:
    print(f"  Tempi: {[round(x,3) for x in peak_times]}")
    intervals = np.diff(peak_times)
    print(f"  Intervalli: {[round(x,3) for x in intervals]}")
    amps = env_norm[peaks]
    print(f"  Ampiezze: {[round(x,3) for x in amps]}")

    # Analisi ampiezze per outlier
    median_amp = np.median(amps)
    mad_amp = np.median(np.abs(amps - median_amp))
    print(f"\nStatistiche ampiezze: median={median_amp:.3f}, MAD={mad_amp:.3f}")
    lower = median_amp - 3.5 * mad_amp
    upper = median_amp + 3.5 * mad_amp
    print(f"  Range accettabile: {lower:.3f} - {upper:.3f}")
    amp_mask = (amps >= lower) & (amps <= upper)
    print(f"  Picchi dentro range: {np.sum(amp_mask)}/{len(amps)}")
    for i, (t, a) in enumerate(zip(peak_times, amps)):
        status = "OK" if amp_mask[i] else "OUTLIER"
        print(f"    {t:.3f}s: {a:.3f} -> {status}")

    # Intervalli per outlier
    if len(intervals) >= 2:
        median_int = np.median(intervals)
        mad_int = np.median(np.abs(intervals - median_int))
        print(f"\nStatistiche intervalli: median={median_int:.3f}s, MAD={mad_int:.3f}s")
        int_lower = max(median_int - 3.0 * mad_int, 0.5 * median_int)
        int_upper = min(median_int + 3.0 * mad_int, 1.5 * median_int)
        print(f"  Range accettabile: {int_lower:.3f}s - {int_upper:.3f}s")
        # Maschera per picchi interni
        valid_mask_int = (intervals >= int_lower) & (intervals <= int_upper)
        print(f"  Intervalli validi: {valid_mask_int.tolist()}")
        keep = np.ones(len(peaks), dtype=bool)
        keep[0] = valid_mask_int[0] if len(valid_mask_int) > 0 else True
        keep[-1] = valid_mask_int[-1] if len(valid_mask_int) > 0 else True
        if len(valid_mask_int) >= 2:
            keep[1:-1] = valid_mask_int[:-1] & valid_mask_int[1:]
        print(f"  Picchi da tenere: {keep.sum()}/{len(keep)}")

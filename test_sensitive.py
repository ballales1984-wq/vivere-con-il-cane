import numpy as np
import librosa
from scipy.signal import butter, filtfilt, hilbert, find_peaks, savgol_filter

def bandpass_filter(signal, fs, low=20, high=150, order=4):
    nyq = fs / 2
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal)

def analyze(filepath):
    y, sr = librosa.load(filepath, sr=None, mono=True, dtype=np.float32)
    duration = len(y) / sr
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

    # Parameters: very sensitive
    threshold_low = max(np.percentile(env_norm, 55), 0.03)
    threshold_low = min(threshold_low, 0.45)
    min_distance_initial = int(0.08 * sr)
    peaks_initial, _ = find_peaks(env_norm, distance=min_distance_initial, height=threshold_low, prominence=0.0002)

    min_distance = int(0.08 * sr)

    if len(peaks_initial) >= 5:
        initial_amplitudes = env_norm[peaks_initial]
        median_amp = np.median(initial_amplitudes)
        mad = np.median(np.abs(initial_amplitudes - median_amp))
        threshold_main = median_amp + 1.0 * mad
        threshold_main = np.clip(threshold_main, 0.04, 0.70)
    else:
        threshold_main = max(np.percentile(env_norm, 60), 0.03)
        threshold_main = min(threshold_main, 0.60)

    peak_to_peak_var = np.std(env_norm[peaks_initial]) if len(peaks_initial) >= 3 else 0.015
    prom = max(0.0002, 0.02 * threshold_main + 0.1 * peak_to_peak_var)
    prom = min(prom, threshold_main * 0.3)

    peaks, properties = find_peaks(env_norm, distance=min_distance, height=threshold_main, prominence=prom)

    if len(peaks) < 2 and len(peaks_initial) >= 2:
        fallback_levels = [(0.95,0.0015),(0.8,0.001),(0.6,0.0005),(0.4,0.0002)]
        for mult, p in fallback_levels:
            lower_thresh = threshold_main * mult
            if lower_thresh < 0.02:
                lower_thresh = 0.02
            peaks, properties = find_peaks(env_norm, distance=min_distance, height=lower_thresh, prominence=p)
            if len(peaks) >= 2:
                break

    if len(peaks) < 2:
        peaks, properties = find_peaks(env_norm, distance=int(0.06 * sr), height=0.015, prominence=0.0001)

    peak_times = (peaks / sr).tolist()
    amplitudes = env_norm[peaks].tolist()
    beat_count_raw = len(peaks)  # numero di picchi rilevati prima di qualsiasi pulizia aggiuntiva

    # Rimozione artefatti iniziali (opzionale, commentato per test)
    # if len(peaks) >= 3:
    #     first_time = peak_times[0]
    #     second_interval = peak_times[1] - peak_times[0]
    #     if first_time < 0.35 and second_interval > 0.5:
    #         peaks = peaks[1:]
    #         peak_times = peak_times[1:]
    #         amplitudes = amplitudes[1:]
    #         beat_count_raw = len(peaks)

    # Validazione fisiologica minima (solo estremi)
    # if beat_count_raw >= 2:
    #     times_arr = np.array(peak_times)
    #     intervals = np.diff(times_arr)
    #     avg_interval = np.mean(intervals)
    #     candidate_bpm = int(60.0 / avg_interval) if avg_interval > 0 else 0
    #     if candidate_bpm > 500:
    #         amp_threshold = np.percentile(amplitudes, 50)
    #         keep = np.array(amplitudes) >= amp_threshold
    #         peaks = peaks[keep]
    #         peak_times = (peaks / sr).tolist()
    #         amplitudes = env_norm[peaks].tolist()
    #         beat_count_raw = len(peaks)
    #     elif candidate_bpm < 15 and beat_count_raw > 5:
    #         amp_threshold = 0.25 * np.max(amplitudes)
    #         keep = np.array(amplitudes) >= amp_threshold
    #         peaks = peaks[keep]
    #         peak_times = (peaks / sr).tolist()
    #         amplitudes = env_norm[peaks].tolist()
    #         beat_count_raw = len(peaks)

    # NESSUNA pulizia outlier aggiuntiva: vogliamo vedere tutti i picchi rilevati
    # Quindi saltiamo la pulizia outlier

    # Calcolo BPM e confidenza da tutti i picchi (supponendo siano tutti S1)
    bpm = 0
    confidence = 0.0
    if beat_count_raw >= 2:
        times_arr = np.array(peak_times)
        intervals = np.diff(times_arr)
        avg_interval = np.mean(intervals)
        bpm = int(60.0 / avg_interval) if avg_interval > 0 else 0
        if len(intervals) > 1:
            std_i = np.std(intervals)
            cv = std_i / (avg_interval + 1e-9)
            reg = max(0.0, 1.0 - cv)
            nsc = min(1.0, beat_count_raw / 20.0)
            confidence = round(0.5 + 0.3*reg + 0.2*nsc, 2)
        else:
            confidence = 0.5
    else:
        bpm = 0
        confidence = 0.0

    envelope_data = None  # non serve

    return {
        'duration': round(duration,2),
        'bpm': bpm,
        'beat_count': beat_count_raw,
        'confidence': confidence,
        'peak_times': peak_times,
        'amplitudes': amplitudes,
        'sample_rate': sr,
        'envelope': None,
    }

res = analyze('test_heart_weak.wav')
print(f"File: test_heart_weak.wav")
print(f"Durata: {res['duration']} s")
print(f"BPM: {res['bpm']}, Confidenza: {res['confidence']}")
print(f"Battiti rilevati: {res['beat_count']}")
print(f"Picchi (s): {[f'{t:.3f}' for t in res['peak_times']]}")
intervals = np.diff(res['peak_times']).tolist() if len(res['peak_times'])>1 else []
print(f"Intervalli (s): {[f'{x:.3f}' for x in intervals]}")
print(f"Range BPM da {60.0/np.max(intervals):.0f} a {60.0/np.min(intervals):.0f}" if intervals else "")

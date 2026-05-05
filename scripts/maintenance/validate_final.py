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

    # Fase 1: detection permissiva
    threshold_low = max(np.percentile(env_norm, 60), 0.04)
    threshold_low = min(threshold_low, 0.5)
    min_distance_initial = int(0.10 * sr)
    peaks_initial, _ = find_peaks(env_norm, distance=min_distance_initial, height=threshold_low, prominence=0.0005)

    # Fase 2: min_distance fisso (120 ms) — non adattivo
    min_distance = int(0.12 * sr)

    # Fase 3: threshold principale
    if len(peaks_initial) >= 5:
        initial_amplitudes = env_norm[peaks_initial]
        median_amp = np.median(initial_amplitudes)
        mad = np.median(np.abs(initial_amplitudes - median_amp))
        threshold_main = median_amp + 1.2 * mad
        threshold_main = np.clip(threshold_main, 0.06, 0.75)
    else:
        threshold_main = max(np.percentile(env_norm, 65), 0.05)
        threshold_main = min(threshold_main, 0.70)

    # Prominence
    peak_to_peak_var = np.std(env_norm[peaks_initial]) if len(peaks_initial) >= 3 else 0.02
    prom = max(0.0005, 0.03 * threshold_main + 0.2 * peak_to_peak_var)
    prom = min(prom, threshold_main * 0.4)

    peaks, properties = find_peaks(env_norm, distance=min_distance, height=threshold_main, prominence=prom)

    # Fallback gerarchico
    if len(peaks) < 2 and len(peaks_initial) >= 2:
        fallback_levels = [(0.9, 0.002), (0.75, 0.001), (0.55, 0.0005), (0.4, 0.0002)]
        for mult, p in fallback_levels:
            lower_thresh = threshold_main * mult
            if lower_thresh < 0.03:
                lower_thresh = 0.03
            peaks, properties = find_peaks(env_norm, distance=min_distance, height=lower_thresh, prominence=p)
            if len(peaks) >= 2:
                break

    if len(peaks) < 2:
        peaks, properties = find_peaks(env_norm, distance=int(0.08 * sr), height=0.02, prominence=0.0002)

    peak_times = (peaks / sr).tolist()
    amplitudes = env_norm[peaks].tolist()
    beat_count = len(peaks)

    # Validazione fisiologica minima (solo estremi)
    if beat_count >= 2:
        times_arr = np.array(peak_times)
        intervals = np.diff(times_arr)
        avg_interval = np.mean(intervals)
        candidate_bpm = int(60.0 / avg_interval) if avg_interval > 0 else 0
        if candidate_bpm > 500:
            amp_threshold = np.percentile(amplitudes, 50)
            keep = np.array(amplitudes) >= amp_threshold
            peaks = peaks[keep]
            peak_times = (peaks / sr).tolist()
            amplitudes = env_norm[peaks].tolist()
            beat_count = len(peaks)
        elif candidate_bpm < 15 and beat_count > 5:
            amp_threshold = 0.25 * np.max(amplitudes)
            keep = np.array(amplitudes) >= amp_threshold
            peaks = peaks[keep]
            peak_times = (peaks / sr).tolist()
            amplitudes = env_norm[peaks].tolist()
            beat_count = len(peaks)

    # Pulizia outlier (conservativa)
    if len(peaks) >= 7:
        peak_times_arr = peaks / sr
        intervals = np.diff(peak_times_arr)
        amplitudes_arr = env_norm[peaks]
        median_amp = np.median(amplitudes_arr)
        mad_amp = np.median(np.abs(amplitudes_arr - median_amp))
        if mad_amp > 1e-6:
            amp_lower = median_amp - 3.5 * mad_amp
            amp_upper = median_amp + 3.5 * mad_amp
            amp_mask = (amplitudes_arr >= amp_lower) & (amplitudes_arr <= amp_upper)
            peaks_f = peaks[amp_mask]
            if len(peaks_f) >= 0.8 * len(peaks):
                peaks = peaks_f
        if len(peaks) >= 7:
            peak_times_arr = peaks / sr
            intervals = np.diff(peak_times_arr)
            if len(intervals) >= 3:
                median_int = np.median(intervals)
                mad_int = np.median(np.abs(intervals - median_int))
                if mad_int > 1e-6:
                    int_lower = max(median_int - 3.0 * mad_int, 0.5 * median_int)
                    int_upper = min(median_int + 3.0 * mad_int, 1.5 * median_int)
                    valid_mask = (intervals >= int_lower) & (intervals <= int_upper)
                    keep = np.ones(len(peaks), dtype=bool)
                    keep[0] = valid_mask[0] if len(valid_mask) > 0 else True
                    keep[-1] = valid_mask[-1] if len(valid_mask) > 0 else True
                    if len(valid_mask) >= 2:
                        keep[1:-1] = valid_mask[:-1] & valid_mask[1:]
                    if np.sum(keep) >= 0.8 * len(peaks):
                        peaks = peaks[keep]
        peak_times = (peaks / sr).tolist()
        amplitudes = env_norm[peaks].tolist()
        beat_count = len(peaks)

    # --- ANALISI BPM/CLASSIFICAZIONE ---
    s1_s2_classification = None
    hrv_metrics = None
    bpm = 0
    confidence = 0.0

    display_peak_times = peak_times
    display_amplitudes = amplitudes

    if beat_count >= 2:
        times_arr = np.array(peak_times)
        amps_arr = np.array(amplitudes)
        intervals_all = np.diff(times_arr)
        short_ratio = np.mean(intervals_all < 0.2) if len(intervals_all) >= 3 else 0
        has_dual = short_ratio >= 0.2

        if has_dual:
            n_pairs = beat_count // 2
            if n_pairs >= 1:
                s1_times_list = []
                s1_amps_list = []
                s2_times_list = []
                s2_amps_list = []
                for i in range(n_pairs):
                    idx1, idx2 = i*2, i*2+1
                    a1, a2 = amps_arr[idx1], amps_arr[idx2]
                    t1, t2 = times_arr[idx1], times_arr[idx2]
                    if a1 >= a2:
                        s1_times_list.append(t1); s1_amps_list.append(a1)
                        s2_times_list.append(t2); s2_amps_list.append(a2)
                    else:
                        s1_times_list.append(t2); s1_amps_list.append(a2)
                        s2_times_list.append(t1); s2_amps_list.append(a1)
                s1_times_arr = np.array(s1_times_list)
                s1_amps_arr = np.array(s1_amps_list)
                if len(s1_times_arr) >= 2:
                    s1_intervals = np.diff(s1_times_arr)
                    avg_s1_int = np.mean(s1_intervals)
                    bpm = int(60.0 / avg_s1_int) if avg_s1_int > 0 else 0
                    if len(s1_intervals) > 1:
                        std_s1 = np.std(s1_intervals)
                        cv = std_s1 / (avg_s1_int + 1e-9)
                        reg_score = max(0.0, 1.0 - cv)
                        n_score = min(1.0, len(s1_times_arr) / 20.0)
                        confidence = round(0.5 + 0.3 * reg_score + 0.2 * n_score, 2)
                    else:
                        confidence = 0.5
                if len(s1_times_arr) >= 3:
                    sdnn = float(np.std(s1_intervals))
                    diff_sq = np.square(np.diff(s1_intervals))
                    rmssd = float(np.sqrt(np.mean(diff_sq))) if len(diff_sq) > 0 else 0.0
                    diff_ms = np.diff(s1_intervals) * 1000.0
                    pnn50 = float(np.mean(np.abs(diff_ms) > 50.0) * 100.0)
                    hrv_metrics = {'sdnn_sec': round(sdnn,4), 'rmssd_sec': round(rmssd,4), 'pnn50_percent': round(pnn50,2), 'mean_hr_sec': round(float(np.mean(s1_intervals)),4)}
                s1_s2_classification = {'s1_count': int(len(s1_times_arr)), 's2_count': int(len(s2_times_list)), 's1_avg_amplitude': float(np.mean(s1_amps_arr)) if len(s1_amps_arr) > 0 else 0.0, 's2_avg_amplitude': float(np.mean(s2_amps_arr)) if len(s2_amps_arr) > 0 else 0.0}
                display_peak_times = s1_times_list
                display_amplitudes = s1_amps_list
                beat_count = len(s1_times_arr)
        else:
            s1_times_arr = times_arr
            intervals_s1 = intervals_all
            avg_s1_int = np.mean(intervals_s1)
            bpm = int(60.0 / avg_s1_int) if avg_s1_int > 0 else 0
            if len(intervals_s1) > 1:
                std_s1 = np.std(intervals_s1)
                cv = std_s1 / (avg_s1_int + 1e-9)
                reg_score = max(0.0, 1.0 - cv)
                n_score = min(1.0, len(s1_times_arr) / 20.0)
                confidence = round(0.5 + 0.3 * reg_score + 0.2 * n_score, 2)
            else:
                confidence = 0.5
            if len(intervals_s1) >= 2:
                sdnn = float(np.std(intervals_s1))
                diff_sq = np.square(np.diff(intervals_s1))
                rmssd = float(np.sqrt(np.mean(diff_sq))) if len(diff_sq) > 0 else 0.0
                diff_ms = np.diff(intervals_s1) * 1000.0
                pnn50 = float(np.mean(np.abs(diff_ms) > 50.0) * 100.0)
                hrv_metrics = {'sdnn_sec': round(sdnn,4), 'rmssd_sec': round(rmssd,4), 'pnn50_percent': round(pnn50,2), 'mean_hr_sec': round(float(np.mean(intervals_s1)),4)}
    else:
        bpm = 0
        confidence = 0.0

    # envelope data per grafico
    t_env = np.arange(len(env_norm)) / sr
    step = max(1, len(env_norm) // 2000)
    envelope_data = {
        "times": t_env[::step].tolist(),
        "values": env_norm[::step].tolist(),
    }

    return {
        'duration': round(duration,2),
        'bpm': bpm,
        'beat_count': beat_count,
        'confidence': confidence,
        'peak_times': display_peak_times,
        'amplitudes': display_amplitudes,
        'sample_rate': sr,
        's1_s2': s1_s2_classification,
        'hrv': hrv_metrics,
        'envelope': envelope_data,
        'filter_low': 20,
        'filter_high': 150,
    }

res = analyze('test_heart_weak.wav')
print(f"BPM: {res['bpm']}, Conf: {res['confidence']}, Battiti: {res['beat_count']}")
if res['s1_s2']:
    print(f"S1/S2: S1={res['s1_s2']['s1_count']}, S2={res['s1_s2']['s2_count']}")
intervals = np.diff(res['peak_times']).tolist() if len(res['peak_times']) > 1 else []
print(f"Intervalli (s): {[round(x,3) for x in intervals]}")
print(f"Picchi (s): {[round(t,3) for t in res['peak_times']]}")
print(f"OK")

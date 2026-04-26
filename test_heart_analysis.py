#!/usr/bin/env python
"""
Standalone test per l'algoritmo di analisi cardiaca.
Esegui: python test_heart_analysis.py
"""

import os
import sys
import numpy as np
import librosa
from scipy.signal import butter, filtfilt, hilbert, find_peaks, savgol_filter

def bandpass_filter(signal, fs, low=20, high=150, order=4):
    nyq = fs / 2
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal)

def analyze_heart_sound(filepath, context=''):
    """Copia dell'algoritmo da views.py per test standalone."""
    try:
        # --- 1. CARICAMENTO ---
        y, sr = librosa.load(filepath, sr=None, mono=True, dtype=np.float32)
        duration = len(y) / sr

        # Normalizza
        y = y / (np.max(np.abs(y)) + 1e-9)

        # --- 2. FILTRO PASSA-BANDA ---
        y_filt = bandpass_filter(y, sr)
        if np.any(np.isnan(y_filt)) or np.any(np.isinf(y_filt)):
            y_filt = y

        # --- 3. ENVELOPE Hilbert + Smoothing ---
        analytic = hilbert(y_filt)
        envelope = np.abs(analytic)

        max_window = 101
        win_len = min(max_window, len(envelope) - 1 if len(envelope) % 2 == 0 else len(envelope))
        if win_len > 3:
            env_max_val = np.max(envelope)
            if env_max_val < 0.05:
                win_len = min(31, win_len)
            if win_len % 2 == 0:
                win_len = max(3, win_len - 1)
            envelope_smooth = savgol_filter(envelope, win_len, 3)
        else:
            envelope_smooth = envelope

        envelope_smooth = np.nan_to_num(envelope_smooth, nan=0.0, posinf=0.0, neginf=0.0)

        # --- 4. NORMALIZZAZIONE ---
        env_min, env_max = np.min(envelope_smooth), np.max(envelope_smooth)
        env_range = env_max - env_min
        if env_range < 1e-6:
            abs_sig = np.abs(y_filt)
            max_abs = np.max(abs_sig)
            if max_abs < 1e-6:
                env_norm = np.zeros_like(envelope_smooth)
            else:
                env_norm = abs_sig / (max_abs + 1e-9)
        else:
            env_norm = (envelope_smooth - env_min) / (env_range + 1e-9)

        env_norm = np.nan_to_num(env_norm, nan=0.0, posinf=0.0, neginf=0.0)
        env_norm = np.clip(env_norm, 0.0, 1.0)

        # ==================== NUOVO ALGORITMO PICCHI ====================
        # Fase 1: stima iniziale permissiva
        threshold_low = np.percentile(env_norm, 70) + 0.05
        threshold_low = min(max(threshold_low, 0.08), 0.6)
        min_distance_initial = int(0.2 * sr)
        peaks_initial, _ = find_peaks(env_norm, distance=min_distance_initial, height=threshold_low, prominence=0.001)

        # Fase 2: stima BPM per min_distance adattivo
        if len(peaks_initial) >= 3:
            peak_times_initial = peaks_initial / sr
            intervals_initial = np.diff(peak_times_initial)
            median_interval = np.median(intervals_initial)
            valid_intervals_mask = (intervals_initial >= 0.5 * median_interval) & (intervals_initial <= 1.5 * median_interval)
            if np.any(valid_intervals_mask):
                median_interval = np.median(intervals_initial[valid_intervals_mask])
            estimated_bpm = int(60.0 / median_interval) if median_interval > 0 else 0
            if 40 <= estimated_bpm <= 220:
                min_distance = max(int(0.4 * median_interval * sr), int(0.15 * sr))
            else:
                min_distance = int(0.3 * sr)
        else:
            min_distance = int(0.3 * sr)

        # Fase 3: threshold principale - robusto (mediana + MAD)
        if len(peaks_initial) >= 5:
            initial_amplitudes = env_norm[peaks_initial]
            median_amp = np.median(initial_amplitudes)
            mad = np.median(np.abs(initial_amplitudes - median_amp))
            threshold_main = median_amp + 1.5 * mad
            threshold_main = np.clip(threshold_main, 0.12, 0.85)
        else:
            mean_amp = np.mean(env_norm)
            std_amp = np.std(env_norm)
            threshold_main = np.clip(mean_amp + 0.4 * std_amp, 0.12, 0.85)

        # Fase 4: prominence adattiva
        peak_to_peak_variation = np.std(env_norm[peaks_initial]) if len(peaks_initial) >= 3 else 0.05
        prom = max(0.003, 0.08 * threshold_main + 0.5 * peak_to_peak_variation)
        prom = min(prom, threshold_main * 0.6)

        # Rilevazione principale
        peaks, properties = find_peaks(env_norm, distance=min_distance, height=threshold_main, prominence=prom)

        # Fase 5: fallback gerarchico
        if len(peaks) < 2 and len(peaks_initial) >= 2:
            fallback_levels = [(0.85, 0.003), (0.7, 0.002), (0.5, 0.001), (0.35, 0.0005)]
            for mult, p in fallback_levels:
                lower_thresh = threshold_main * mult
                if lower_thresh < 0.06:
                    lower_thresh = 0.06
                peaks, properties = find_peaks(env_norm, distance=min_distance, height=lower_thresh, prominence=p)
                if len(peaks) >= 2:
                    break

        if len(peaks) < 2:
            peaks, properties = find_peaks(env_norm, distance=int(0.25 * sr), height=0.03, prominence=0.0005)

        peak_times = (peaks / sr).tolist()
        amplitudes = env_norm[peaks].tolist()
        beat_count = len(peaks)

        # Validazione fisiologica
        if beat_count >= 2:
            times_arr = np.array(peak_times)
            intervals = np.diff(times_arr)
            avg_interval = np.mean(intervals)
            candidate_bpm = int(60.0 / avg_interval) if avg_interval > 0 else 0

            if candidate_bpm > 350:
                high_freq_mask = amplitudes >= np.percentile(amplitudes, 60)
                peaks = peaks[high_freq_mask]
                peak_times = (peaks / sr).tolist()
                amplitudes = env_norm[peaks].tolist()
                beat_count = len(peaks)
            elif candidate_bpm < 25 and beat_count > 5:
                amp_threshold = 0.15 * np.max(amplitudes)
                keep_mask = np.array(amplitudes) >= amp_threshold
                peaks = peaks[keep_mask]
                peak_times = (peaks / sr).tolist()
                amplitudes = env_norm[peaks].tolist()
                beat_count = len(peaks)

        # Pulizia outlier robusta
        if len(peaks) >= 5:
            peak_times_arr = peaks / sr
            intervals = np.diff(peak_times_arr)

            amplitudes_arr = env_norm[peaks]
            median_amp = np.median(amplitudes_arr)
            mad_amp = np.median(np.abs(amplitudes_arr - median_amp))
            amp_lower = median_amp - 3 * (mad_amp + 1e-9)
            amp_upper = median_amp + 3 * (mad_amp + 1e-9)
            amp_mask = (amplitudes_arr >= amp_lower) & (amplitudes_arr <= amp_upper)
            peaks = peaks[amp_mask]

            if len(peaks) >= 5:
                peak_times_arr = peaks / sr
                intervals = np.diff(peak_times_arr)
                median_int = np.median(intervals)
                mad_int = np.median(np.abs(intervals - median_int))

                if mad_int < 0.01:
                    int_lower = 0.5 * median_int
                    int_upper = 1.5 * median_int
                else:
                    int_lower = median_int - 2.5 * mad_int
                    int_upper = median_int + 2.5 * mad_int

                if len(intervals) >= 3:
                    valid_mask_intervals = (intervals >= int_lower) & (intervals <= int_upper)
                    keep = np.ones(len(peaks), dtype=bool)
                    if len(valid_mask_intervals) > 0:
                        keep[0] = valid_mask_intervals[0]
                    if len(valid_mask_intervals) >= 2:
                        keep[1:-1] = valid_mask_intervals[:-1] & valid_mask_intervals[1:]
                    if len(valid_mask_intervals) > 0:
                        keep[-1] = valid_mask_intervals[-1]
                    peaks = peaks[keep]

            peak_times = (peaks / sr).tolist()
            amplitudes = env_norm[peaks].tolist()
            beat_count = len(peaks)

        # ==================== ANALISI BPM/CLASSIFICAZIONE ====================
        s1_s2_classification = None
        hrv_metrics = None
        bpm = 0
        confidence = 0.0

        if beat_count >= 2:
            times_arr = np.array(peak_times)
            amps_arr = np.array(amplitudes)
            intervals_all = np.diff(times_arr)

            if len(intervals_all) >= 3:
                short_ratio = np.mean(intervals_all < 0.2)
                has_dual_components = short_ratio >= 0.2
            else:
                has_dual_components = False

            if has_dual_components:
                n_pairs = beat_count // 2
                if n_pairs >= 1:
                    s1_times = []
                    s1_amps = []
                    s2_times = []
                    s2_amps = []

                    for i in range(n_pairs):
                        idx1 = i * 2
                        idx2 = i * 2 + 1
                        a1 = amps_arr[idx1]
                        a2 = amps_arr[idx2]
                        t1 = times_arr[idx1]
                        t2 = times_arr[idx2]
                        if a1 >= a2:
                            s1_times.append(t1)
                            s1_amps.append(a1)
                            s2_times.append(t2)
                            s2_amps.append(a2)
                        else:
                            s1_times.append(t2)
                            s1_amps.append(a2)
                            s2_times.append(t1)
                            s2_amps.append(a1)

                    s1_times = np.array(s1_times)
                    s1_amps = np.array(s1_amps)
                    s2_times = np.array(s2_times)
                    s2_amps = np.array(s2_amps)

                    if len(s1_times) >= 2:
                        s1_intervals = np.diff(s1_times)
                        avg_s1_int = np.mean(s1_intervals)
                        bpm = int(60.0 / avg_s1_int) if avg_s1_int > 0 else 0
                        if len(s1_intervals) > 1:
                            std_s1 = np.std(s1_intervals)
                            cv = std_s1 / (avg_s1_int + 1e-9)
                            reg_score = max(0.0, 1.0 - cv)
                            n_score = min(1.0, len(s1_times) / 20.0)
                            confidence = round(0.5 + 0.3 * reg_score + 0.2 * n_score, 2)
                        else:
                            confidence = 0.5
                    else:
                        confidence = 0.0

                    if len(s1_times) >= 3:
                        sdnn = float(np.std(s1_intervals))
                        diff_sq = np.square(np.diff(s1_intervals))
                        rmssd = float(np.sqrt(np.mean(diff_sq))) if len(diff_sq) > 0 else 0.0
                        diff_ms = np.diff(s1_intervals) * 1000.0
                        pnn50 = float(np.mean(np.abs(diff_ms) > 50.0) * 100.0)
                        hrv_metrics = {
                            "sdnn_sec": round(sdnn, 4),
                            "rmssd_sec": round(rmssd, 4),
                            "pnn50_percent": round(pnn50, 2),
                            "mean_hr_sec": round(float(np.mean(s1_intervals)), 4),
                        }

                    s1_s2_classification = {
                        "s1_count": int(len(s1_times)),
                        "s2_count": int(len(s2_times)),
                        "s1_avg_amplitude": float(np.mean(s1_amps)) if len(s1_amps) > 0 else 0.0,
                        "s2_avg_amplitude": float(np.mean(s2_amps)) if len(s2_amps) > 0 else 0.0,
                    }
                    beat_count = len(s1_times)
                else:
                    bpm = int(60.0 / np.mean(intervals_all)) if np.mean(intervals_all) > 0 else 0
                    confidence = 0.5
            else:
                s1_times = times_arr
                intervals_s1 = intervals_all
                avg_s1_int = np.mean(intervals_s1)
                bpm = int(60.0 / avg_s1_int) if avg_s1_int > 0 else 0
                if len(intervals_s1) > 1:
                    std_s1 = np.std(intervals_s1)
                    cv = std_s1 / (avg_s1_int + 1e-9)
                    reg_score = max(0.0, 1.0 - cv)
                    n_score = min(1.0, len(s1_times) / 20.0)
                    confidence = round(0.5 + 0.3 * reg_score + 0.2 * n_score, 2)
                else:
                    confidence = 0.5
                if len(intervals_s1) >= 2:
                    sdnn = float(np.std(intervals_s1))
                    diff_sq = np.square(np.diff(intervals_s1))
                    rmssd = float(np.sqrt(np.mean(diff_sq))) if len(diff_sq) > 0 else 0.0
                    diff_ms = np.diff(intervals_s1) * 1000.0
                    pnn50 = float(np.mean(np.abs(diff_ms) > 50.0) * 100.0)
                    hrv_metrics = {
                        "sdnn_sec": round(sdnn, 4),
                        "rmssd_sec": round(rmssd, 4),
                        "pnn50_percent": round(pnn50, 2),
                        "mean_hr_sec": round(float(np.mean(intervals_s1)), 4),
                    }
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
            "duration": round(duration, 2),
            "bpm": bpm,
            "beat_count": beat_count,
            "confidence": confidence,
            "peak_times": peak_times,
            "amplitudes": amplitudes,
            "sample_rate": sr,
            "s1_s2": s1_s2_classification,
            "hrv": hrv_metrics,
            "envelope": envelope_data,
            "filter_low": 20,
            "filter_high": 150,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


if __name__ == "__main__":
    test_file = "test_heart_weak.wav"
    if not os.path.exists(test_file):
        print(f"File di test '{test_file}' non trovato nella directory corrente")
        sys.exit(1)

    print(f"Analisi di: {test_file}")
    result = analyze_heart_sound(test_file)

    if "error" in result:
        print(f"ERRORE: {result['error']}")
        sys.exit(1)

    print("\n=== RISULTATI ANALISI ===")
    print(f"Durata: {result['duration']} s")
    print(f"BPM: {result['bpm']}")
    print(f"Battiti totali: {result['beat_count']}")
    print(f"Confidenza: {result['confidence']}")
    print(f"Sample rate: {result['sample_rate']} Hz")

    if result.get('s1_s2'):
        print(f"\n--- S1/S2 ---")
        print(f"  S1: {result['s1_s2']['s1_count']} (amp: {result['s1_s2']['s1_avg_amplitude']:.3f})")
        print(f"  S2: {result['s1_s2']['s2_count']} (amp: {result['s1_s2']['s2_avg_amplitude']:.3f})")

    if result.get('hrv'):
        print(f"\n--- HRV ---")
        print(f"  SDNN: {result['hrv']['sdnn_sec']} s")
        print(f"  RMSSD: {result['hrv']['rmssd_sec']} s")
        print(f"  pNN50: {result['hrv']['pnn50_percent']}%")

    print(f"\nPicchi rilevati: {len(result['peak_times'])}")
    if result['peak_times']:
        print(f"  Primi 5: {[f'{t:.3f}s' for t in result['peak_times'][:5]]}")
        print(f"  Ultimi 5: {[f'{t:.3f}s' for t in result['peak_times'][-5:]]}")

    # Controlli di validità
    print("\n=== VALIDATION ===")
    if result['bpm'] > 0:
        if 60 <= result['bpm'] <= 140:
            print("[OK] BPM in range cane adulto (60-140)")
        elif 100 <= result['bpm'] <= 200:
            print("[OK] BPM in range cane piccolo/giovane (100-200)")
        elif 40 <= result['bpm'] < 60:
            print("[OK] BPM in range cane grande/riposo (40-60)")
        else:
            print(f"[WARN] BPM {result['bpm']} fuori range comune (40-200)")
    else:
        print("[ERR] BPM nullo - nessun battito rilevato")

    if result['confidence'] >= 0.7:
        print("[OK] Confidenza alta")
    elif result['confidence'] >= 0.5:
        print("[WARN] Confidenza media")
    else:
        print("[ERR] Confidenza bassa")

    # Plot opzionale - disabilitato per evitare errori matplotlib
    # Salva comunque un report testuale
    with open('heart_analysis_report.txt', 'w') as f:
        f.write(f"File: {test_file}\n")
        f.write(f"Durata: {result['duration']} s\n")
        f.write(f"BPM: {result['bpm']}\n")
        f.write(f"Battiti: {result['beat_count']}\n")
        f.write(f"Confidenza: {result['confidence']}\n")
        f.write(f"Picchi: {result['peak_times']}\n")
        if result.get('s1_s2'):
            f.write(f"S1: {result['s1_s2']['s1_count']}, S2: {result['s1_s2']['s2_count']}\n")
    print("[REPORT] Dettagli salvati in: heart_analysis_report.txt")

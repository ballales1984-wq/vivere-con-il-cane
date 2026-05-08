"""
Heart Sound Analysis Service
Pipeline di analisi fonocardiografica digitale per cani e umani.
Estratto da canine_tools.views per separazione delle responsabilità.
"""

import os
import tempfile
import numpy as np
from scipy.signal import butter, filtfilt, hilbert, find_peaks, savgol_filter
import librosa


def bandpass_filter(signal, fs, low=20, high=150, order=4):
    """Filtro Butterworth passa-banda."""
    nyq = fs / 2
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal)


def analyze_heart_sound(filepath, context='', subject_type='dog'):
    """
    Analisi avanzata di fonocardiografia digitale.
    
    Pipeline:
    1. Caricamento audio (supporta WebM/MP3/WAV via pydub o librosa)
    2. Filtro passa-banda 20-150 Hz (Butterworth 4° ordine)
    3. Envelope Hilbert + Savitzky-Golay smoothing
    4. Rilevamento picchi con threshold adattivo (MAD-based)
    5. Classificazione S1/S2 (se dual-component)
    6. Calcolo HRV (SDNN, RMSSD, pNN50)
    7. Confidence scoring (regolarità + numero cicli)
    
    Args:
        filepath: Path al file audio (WebM, WAV, MP3, etc.)
        context: Contesto registrazione (rest, after_activity, etc.)
        subject_type: 'dog' o 'human' per range BPM normali
        
    Returns:
        Dict con: duration, bpm, beat_count, confidence, peak_times,
                  amplitudes, sample_rate, s1_s2, hrv, envelope,
                  filter_low, filter_high
    """
    try:
        # --- 1. CARICAMENTO ---
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext in ('.webm', '.ogg', '.mp3', '.m4a', '.flac', '.wma', '.aac'):
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(filepath)
                if audio.channels == 2:
                    audio = audio.set_channels(1)
                if audio.sample_width != 2:
                    audio = audio.set_sample_width(2)
                samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
                samples = samples / 32768.0
                y = samples
                sr = audio.frame_rate
            except ImportError:
                raise ImportError("pydub non installato. pip install pydub")
            except Exception as e:
                error_msg = str(e).lower()
                if "ffmpeg" in error_msg or "avconv" in error_msg or "file could not be identified" in error_msg:
                    raise RuntimeError(
                        "Impossibile processare il file audio. "
                        "Assicurati che FFmpeg sia installato e nel PATH. "
                        "Download: https://ffmpeg.org/download.html"
                    )
                try:
                    import librosa
                    y, sr = librosa.load(filepath, sr=None, mono=True, dtype=np.float32)
                except Exception as librosa_error:
                    raise RuntimeError(
                        f"Errore lettura file audio con pydub: {e}. "
                        f"Fallback librosa fallito: {librosa_error}"
                    )
        else:
            import librosa
            y, sr = librosa.load(filepath, sr=None, mono=True, dtype=np.float32)
        
        duration = len(y) / sr
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
        
        # --- 5. RILEVAMENTO PICCHI ---
        threshold_low = max(np.percentile(env_norm, 55), 0.03)
        threshold_low = min(threshold_low, 0.45)
        
        min_distance_initial = int(0.08 * sr)
        peaks_initial, _ = find_peaks(
            env_norm, distance=min_distance_initial, 
            height=threshold_low, prominence=0.0002
        )
        
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
        
        peaks, properties = find_peaks(
            env_norm, distance=min_distance, 
            height=threshold_main, prominence=prom
        )
        
        # Fallback gerarchico
        if len(peaks) < 2 and len(peaks_initial) >= 2:
            fallback_levels = [
                (0.95, 0.0015),
                (0.8, 0.001),
                (0.6, 0.0005),
                (0.4, 0.0002),
            ]
            for mult, p in fallback_levels:
                lower_thresh = threshold_main * mult
                if lower_thresh < 0.02:
                    lower_thresh = 0.02
                peaks, properties = find_peaks(
                    env_norm, distance=min_distance,
                    height=lower_thresh, prominence=p
                )
                if len(peaks) >= 2:
                    break
        
        if len(peaks) < 2:
            peaks, properties = find_peaks(
                env_norm, distance=int(0.06 * sr), 
                height=0.015, prominence=0.0001
            )
        
        # Calcola tempi e ampiezze
        peak_times = (peaks / sr).tolist()
        amplitudes = env_norm[peaks].tolist()
        beat_count = len(peaks)
        
        # --- 6. PULIZIA OUTLIER ---
        if len(peaks) >= 7:
            peak_times_arr = peaks / sr
            intervals = np.diff(peak_times_arr)
            
            # Pulizia ampiezze (MAD conservativo)
            amplitudes_arr = env_norm[peaks]
            median_amp = np.median(amplitudes_arr)
            mad_amp = np.median(np.abs(amplitudes_arr - median_amp))
            amp_lower = median_amp - 3.5 * (mad_amp + 1e-9)
            amp_upper = median_amp + 3.5 * (mad_amp + 1e-9)
            amp_mask = (amplitudes_arr >= amp_lower) & (amplitudes_arr <= amp_upper)
            peaks_filtered = peaks[amp_mask]
            
            if len(peaks_filtered) >= 0.8 * len(peaks):
                peaks = peaks_filtered
            
            # Pulizia intervalli
            if len(peaks) >= 7:
                peak_times_arr = peaks / sr
                intervals = np.diff(peak_times_arr)
                median_int = np.median(intervals)
                mad_int = np.median(np.abs(intervals - median_int))
                
                if mad_int < 0.01:
                    int_lower = 0.5 * median_int
                    int_upper = 1.5 * median_int
                else:
                    int_lower = median_int - 3.0 * mad_int
                    int_upper = median_int + 3.0 * mad_int
                
                int_lower = max(int_lower, 0.5 * median_int)
                int_upper = min(int_upper, 1.5 * median_int)
                
                if len(intervals) >= 3:
                    valid_mask_intervals = (intervals >= int_lower) & (intervals <= int_upper)
                    keep = np.ones(len(peaks), dtype=bool)
                    if len(valid_mask_intervals) > 0:
                        keep[0] = valid_mask_intervals[0]
                    if len(valid_mask_intervals) >= 2:
                        keep[1:-1] = valid_mask_intervals[:-1] & valid_mask_intervals[1:]
                    if len(valid_mask_intervals) > 0:
                        keep[-1] = valid_mask_intervals[-1]
                    
                    if np.sum(keep) >= 0.8 * len(peaks):
                        peaks = peaks[keep]
            
            peak_times = (peaks / sr).tolist()
            amplitudes = env_norm[peaks].tolist()
            beat_count = len(peaks)
        
        # --- 7. ANALISI BPM E CLASSIFICAZIONE ---
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
            
            candidate_bpm_direct = int(60.0 / np.mean(intervals_all)) if np.mean(intervals_all) > 0 else 0
            
            if len(intervals_all) >= 3:
                short_ratio = np.mean(intervals_all < 0.2)
                has_dual_components = short_ratio >= 0.2
            else:
                has_dual_components = False
            
            if subject_type == 'human' and candidate_bpm_direct > 0 and candidate_bpm_direct < 50:
                has_dual_components = False
            
            if has_dual_components and subject_type != 'human':
                n_pairs = beat_count // 2
                if n_pairs >= 1:
                    s1_times_list = []
                    s1_amps_list = []
                    s2_times_list = []
                    s2_amps_list = []
                    
                    for i in range(n_pairs):
                        idx1 = i * 2
                        idx2 = i * 2 + 1
                        a1 = amps_arr[idx1]
                        a2 = amps_arr[idx2]
                        t1 = times_arr[idx1]
                        t2 = times_arr[idx2]
                        if a1 >= a2:
                            s1_times_list.append(t1)
                            s1_amps_list.append(a1)
                            s2_times_list.append(t2)
                            s2_amps_list.append(a2)
                        else:
                            s1_times_list.append(t2)
                            s1_amps_list.append(a2)
                            s2_times_list.append(t1)
                            s2_amps_list.append(a1)
                    
                    s1_times_arr = np.array(s1_times_list)
                    s1_amps_arr = np.array(s1_amps_list)
                    s2_times_arr = np.array(s2_times_list)
                    s2_amps_arr = np.array(s2_amps_list)
                    
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
                    else:
                        confidence = 0.0
                    
                    if len(s1_times_arr) >= 3:
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
                        "s1_count": int(len(s1_times_arr)),
                        "s2_count": int(len(s2_times_arr)),
                        "s1_avg_amplitude": float(np.mean(s1_amps_arr)) if len(s1_amps_arr) > 0 else 0.0,
                        "s2_avg_amplitude": float(np.mean(s2_amps_arr)) if len(s2_amps_arr) > 0 else 0.0,
                    }
                    
                    display_peak_times = s1_times_list
                    display_amplitudes = s1_amps_list
                    beat_count = len(s1_times_arr)
                else:
                    bpm = int(60.0 / np.mean(intervals_all)) if np.mean(intervals_all) > 0 else 0
                    confidence = 0.5
            else:
                s1_times_arr = times_arr
                intervals_s1 = intervals_all
                avg_s1_int = np.mean(intervals_s1)
                bpm = int(60.0 / avg_s1_int) if avg_s1_int > 0 else 0
                
                if len(intervals_s1) >= 1:
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
                    hrv_metrics = {
                        "sdnn_sec": round(sdnn, 4),
                        "rmssd_sec": round(rmssd, 4),
                        "pnn50_percent": round(pnn50, 2),
                        "mean_hr_sec": round(float(np.mean(intervals_s1)), 4),
                    }
        else:
            bpm = 0
            confidence = 0.0
        
        # --- 8. ENVELOPE DATA per grafico ---
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
            "peak_times": display_peak_times,
            "amplitudes": display_amplitudes,
            "sample_rate": sr,
            "s1_s2": s1_s2_classification,
            "hrv": hrv_metrics,
            "envelope": envelope_data,
            "filter_low": 20,
            "filter_high": 150,
        }
        
    except ImportError as e:
        raise ImportError(
            "Dipendenze mancanti per l'analisi audio. "
            "Installa: pip install numpy scipy librosa pydub\n"
            f"Errore originale: {e}"
        )

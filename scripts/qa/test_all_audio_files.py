#!/usr/bin/env python
"""
Test script per analizzare TUTTI i file audio WAV registrati.
Cerca file WAV in tutte le sottocartelle e testa heart_analyze.
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from canine_tools.views import analyze_heart_sound
import glob

def find_all_wav_files():
    """Cerca tutti i file WAV nel progetto, inclusi in sottocartelle."""
    wav_files = []
    
    # Cerca nella root
    wav_files.extend(glob.glob("*.wav"))
    
    # Cerca in tutte le sottocartelle
    for root, dirs, files in os.walk('.'):
        # Escludi cartelle di sistema
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.venv', 'venv', 'env']]
        
        for file in files:
            if file.endswith('.wav'):
                full_path = os.path.join(root, file)
                wav_files.append(full_path)
    
    return sorted(set(wav_files))

def test_audio_file(file_path, file_num, total):
    """Testa un singolo file audio."""
    print(f"\n{'='*70}")
    print(f"File {file_num}/{total}: {file_path}")
    print(f"{'='*70}")
    
    try:
        # Ottieni info file
        file_size = os.path.getsize(file_path)
        print(f"Dimensione: {file_size / 1024:.1f} KB")
        
        # Esegui analisi
        result = analyze_heart_sound(file_path, context="Test batch da script")
        
        # Stampa risultati
        print(f"\n[SUCCESS] Analisi completata!")
        print(f"  Durata:     {result.get('duration', 0):.2f} sec")
        print(f"  BPM:        {result.get('bpm', 0)}")
        print(f"  Battiti:    {result.get('beat_count', 0)}")
        print(f"  Confidenza: {result.get('confidence', 0):.2f}")
        print(f"  Sample rate: {result.get('sample_rate', 'N/A')}")
        
        s1_s2 = result.get('s1_s2')
        if s1_s2:
            print(f"\n  S1: {s1_s2.get('s1_count', 0)} battiti (amp: {s1_s2.get('s1_avg_amplitude', 0):.3f})")
            print(f"  S2: {s1_s2.get('s2_count', 0)} battiti (amp: {s1_s2.get('s2_avg_amplitude', 0):.3f})")
        
        hrv = result.get('hrv')
        if hrv:
            print(f"\n  HRV - SDNN: {hrv.get('sdnn_sec', 0):.4f}s, RMSSD: {hrv.get('rmssd_sec', 0):.4f}s")
        
        peaks = result.get('peak_times', [])
        print(f"\n  Picchi totali rilevati: {len(peaks)}")
        if len(peaks) > 0:
            print(f"  Intervallo medio: {(peaks[-1] - peaks[0]) / max(len(peaks)-1, 1):.2f} sec")
            if len(peaks) > 3:
                print(f"  Primi 5 picchi: {[f'{p:.2f}' for p in peaks[:5]]}")
        
        return True, result
        
    except Exception as e:
        print(f"\n[FAILED] Errore: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def main():
    print("\n" + "="*70)
    print("TEST BATCH: Analisi file audio WAV registrati")
    print("="*70)
    
    # Trova tutti i file WAV
    wav_files = find_all_wav_files()
    
    if not wav_files:
        print("\nNessun file WAV trovato nel progetto!")
        print("Cerca in:")
        print("  - cartella principale")
        print("  - sottocartelle")
        return
    
    print(f"\nTrovati {len(wav_files)} file WAV:")
    for i, f in enumerate(wav_files, 1):
        print(f"  {i}. {f}")
    
    # Testa ogni file
    results = []
    for i, file_path in enumerate(wav_files, 1):
        success, result = test_audio_file(file_path, i, len(wav_files))
        results.append((file_path, success, result))
    
    # Riepilogo
    print(f"\n{'='*70}")
    print("RIEPILOGO TEST")
    print(f"{'='*70}")
    
    success_count = sum(1 for _, s, _ in results if s)
    print(f"\nFile testati: {len(results)}")
    print(f"Riusciti:     {success_count}")
    print(f"Falliti:      {len(results) - success_count}")
    
    print(f"\nDettagli:")
    for file_path, success, result in results:
        status = "OK" if success else "FAIL"
        bpm = f"{result.get('bpm', 0)} BPM" if result and success else "N/A"
        print(f"  [{status}] {file_path} - {bpm}")
    
    print(f"\n{'='*70}")
    if success_count == len(results):
        print("TUTTI I TEST SONO PASSATI! Tool cuore OK!")
    else:
        print(f"Alcuni test sono falliti. Controlla gli errori sopra.")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()

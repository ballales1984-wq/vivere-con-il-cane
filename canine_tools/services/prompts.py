"""
AI Prompt Templates
Template system messages e prompt per i vari use-case dell'app.
"""

from django.utils import translation


def get_daily_coach_prompt(history_text: str, lang: str = "it") -> tuple[str, str]:
    """
    Costruisce prompt per Daily Coach.
    
    Returns:
        (system_msg, user_prompt)
    """
    if lang == "en":
        system_msg = (
            "You are an 'AI Daily Coach' for dogs. "
            "Provide 2 BRIEF tips (max 15 words each) and very practical "
            "for today's session, based on recent trends AND any recent medical issues. "
            "Be encouraging."
        )
        user_prompt = (
            f"Analyze the history and recent medical events and give me 2 tips for today.\n"
            f"{history_text}\n\n"
            f"Respond EXACTLY as a JSON array of strings, e.g.: "
            f'["tip 1", "tip 2"]. Nothing else.'
        )
    else:
        system_msg = (
            "Sei un 'AI Daily Coach' per cani. Fornisci 2 consigli BREVI "
            "(max 15 parole l'uno) e molto pratici per la giornata di oggi, "
            "basati sui trend degli ultimi giorni E sugli eventuali problemi medici recenti segnalati. Sii incoraggiante."
        )
        user_prompt = (
            f"Analizza lo storico e gli eventi medici recenti e dammi 2 consigli per oggi.\n"
            f"{history_text}\n\n"
            f"Rispondi ESATTAMENTE con un array JSON di stringhe, es: "
            f'["consiglio 1", "consiglio 2"]. Niente altro.'
        )
    
    return system_msg, user_prompt


def get_problem_analysis_prompt(context: str, lang: str = "it") -> str:
    """
    Prompt principale per analisi problemi comportamentali.
    
    Args:
        context: Contesto completo (descrizione + dati cane + breed + medical history)
        lang: 'it' o 'en'
    """
    if lang == "en":
        prompt = f"""You are an expert in canine behavior and wellness. Analyze this problem and provide a practical and personalized response.

{context}

Provide:
1. most likely cause
2. 2-3 practical solutions
3. a specific tip for this dog
4. when to consult a veterinarian

Answer in English clearly and practically."""
    else:
        prompt = f"""Sei un esperto di comportamento e benessere canino. Analizza questo problema e fornisci una risposta pratica e personalizzata.

{context}

Fornisci:
1. causa più probabile
2. 2-3 soluzioni pratiche
3. un consiglio specifico per questo cane
4. quando consultare un veterinario

Rispondi in italiano in modo chiaro e pratico."""
    
    return prompt


SYSTEM_PROMPT_DOG_EXPERT = "Sei un esperto di cani gentile e pratico."
SYSTEM_PROMPT_VET_CARDIOLOGIST = "Sei un veterinario specializzato in cardiologia animale. Rispondi in italiano, conciso, max 150 parole."


def get_macro_analysis_prompt(context_json: str) -> str:
    """
    Prompt per macro-analisi lifetime (report completo).
    
    Args:
        context_json: JSON con dati aggregati del cane
    """
    return (
        "Sei un Esperto Veterinario Analista e Comportamentalista.\n"
        "Il tuo compito è leggere i dati aggregati di TUTTA LA VITA di questo cane "
        "e generare un Report Macro (Check-up Totale).\n"
        "Devi restituire SOLO codice HTML puro (senza markdown ```html), "
        "formattato elegantemente, diviso esattamente in queste 4 sezioni:\n"
        "<h2>1. Valutazione Stile di Vita</h2> "
        "(Analizza sonno, passeggiate, gioco basandoti sulle medie)\n"
        "<h2>2. Correlazioni Clinico-Comportamentali</h2> "
        "(Trova schemi tra eventi medici e problemi)\n"
        "<h2>3. Segnali d'Allarme (Red Flags)</h2> "
        "(Anomalie o carenze rispetto agli standard di razza)\n"
        "<h2>4. Protocollo Benessere Prossimi 3 Mesi</h2> "
        "(Azioni a lungo termine)\n\n"
        f"Analizza questo Gemello Digitale (Dati di Vita):\n{context_json}"
    )


def get_vet_summary_context(dog, analysis, problem_desc: str, recent_events: list) -> str:
    """
    Costruisce il contesto per il riassunto veterinario.
    
    Returns:
        Stringa formattata con tutti i dati clinici rilevanti
    """
    summary = f"RIASSUNTO CLINICO - {dog.dog_name}\n"
    summary += f"Razza: {dog.breed or 'N/A'} | Età: {dog.get_age()} anni | Peso: {dog.weight or 'N/A'} kg\n"
    summary += f"Problema: {problem_desc[:200]}\n\n"
    
    if analysis and analysis.ai_response:
        summary += "ANALISI AI:\n"
        summary += analysis.ai_response[:500] + "...\n"
    
    if recent_events:
        summary += "\nEVENTI MEDICI RECENTI:\n"
        for event in recent_events[:3]:
            summary += f"- {event.date.strftime('%d/%m/%Y')}: {event.title}\n"
    
    return summary


def get_heart_analysis_prompt(subject_name: str, subject_type: str, 
                               subject_weight: str, context_display: str,
                               duration: float, bpm: int, beat_count: int,
                               confidence: float, hrv: Optional[Dict],
                               s1_s2: Optional[Dict]) -> str:
    """
    Prompt per analisi cardiaca con LLM.
    
    Returns:
        Prompt completo per veterinario cardio esperto
    """
    prompt = f"""Sei un veterinario specializzato in cardiologia animale. Analizza questi dati di fonocardiografia.

**Dati:**
- Soggetto: {subject_name} ({'cane' if subject_type=='dog' else 'umano'})
- Peso: {subject_weight}
- Contesto: {context_display}
- Durata: {duration} s
- BPM: {bpm}
- Battiti (S1): {beat_count}
- Confidenza: {confidence:.2f}

**HRV:**"""
    
    if hrv:
        h = hrv
        prompt += f" SDNN={h['sdnn_sec']}s, RMSSD={h['rmssd_sec']}s, pNN50={h['pnn50_percent']}%"
    else:
        prompt += " Non disponibile."
    
    s1_s2_ratio = "N/A"
    if s1_s2 and s1_s2.get('s2_avg_amplitude', 0) > 0:
        s1_s2_ratio = f"{s1_s2['s1_avg_amplitude'] / s1_s2['s2_avg_amplitude']:.2f}"
    
    prompt += f"""
**S1/S2:** S1={s1_s2['s1_count'] if s1_s2 else 'N/A'}, S2={s1_s2['s2_count'] if s1_s2 else 'N/A'}, Rapporto={s1_s2_ratio}

Fornisci 4 punti:
1. Stato attuale (normale/stressato/patologico)
2. Confronto BPM con range normale ({subject_weight if subject_type=='dog' else '60-100 BPM'})
3. Significato HRV e S1/S2
4. Consigli pratici

Max 150 parole, italiano chiaro."""
    
    return prompt

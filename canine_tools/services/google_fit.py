"""
Google Fit / Health Connect Service
Sincronizzazione dati fitness da Google APIs.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import json


def build_time_range(days: int = 7) -> tuple[int, int]:
    """
    Costruisce l'intervallo di tempo per l'API (nanoseconds).
    
    Args:
        days: numero di giorni indietro da cui recuperare dati
        
    Returns:
        (start_ns, end_ns) timestamp in nanoseconds
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    start_ns = int(start_time.timestamp() * 1e9)
    end_ns = int(end_time.timestamp() * 1e9)
    return start_ns, end_ns


def sync_via_fitness_api(creds, user, dogs, days: int = 30) -> Dict[str, Any]:
    """
    Sincronizza usando Google Fit API (legacy, ma ancora funzionante).
    Recupera: passi, distanza, calorie, frequenza cardiaca.
    
    Args:
        creds: Google OAuth credentials
        user: Utente Django
        dogs: QuerySet di DogProfile dell'utente
        days: Giorni indietro per cui sincronizzare
        
    Returns:
        Dict con {saved, skipped, errors}
    """
    from googleapiclient.discovery import build
    
    service = build('fitness', 'v1', credentials=creds)
    
    saved_count = 0
    skipped = 0
    errors = []
    start_ns, end_ns = build_time_range(days)
    
    for dog in dogs:
        try:
            # STEP 1: Steps (passi)
            try:
                aggregate_body = {
                    "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
                    "bucketByTime": {"durationMillis": 86400000},  # 1 giorno
                    "startTimeMillis": int(start_ns / 1e6),
                    "endTimeMillis": int(end_ns / 1e6),
                }
                
                agg_response = service.users().dataset().aggregate(
                    userId='me',
                    body=aggregate_body
                ).execute()
                
                for bucket in agg_response.get('bucket', []):
                    start_ms = int(bucket.get('startTimeMillis', 0))
                    end_ms = int(bucket.get('endTimeMillis', 0))
                    
                    steps = 0
                    for point in bucket.get('point', []):
                        for value in point.get('value', []):
                            if 'intVal' in value:
                                steps += value['intVal']
                    
                    if steps > 0:
                        from canine_tools.models import HealthDataPoint
                        start_dt = datetime.utcfromtimestamp(start_ms / 1000)
                        end_dt = datetime.utcfromtimestamp(end_ms / 1000)
                        
                        HealthDataPoint.objects.update_or_create(
                            dog=dog,
                            user=user,
                            source_type='steps',
                            start_time=start_dt,
                            end_time=end_dt,
                            defaults={
                                'value': float(steps),
                                'unit': 'steps',
                                'data_source_name': 'Google Fit (aggregated)',
                            }
                        )
                        saved_count += 1
            
            except Exception as api_err:
                errors.append(f"Steps API error for {dog.dog_name}: {str(api_err)}")
            
            # STEP 2: Heart rate
            try:
                hr_body = {
                    "aggregateBy": [{"dataTypeName": "com.google.heart_rate.bpm"}],
                    "bucketByTime": {"durationMillis": 86400000},
                    "startTimeMillis": int(start_ns / 1e6),
                    "endTimeMillis": int(end_ns / 1e6),
                }
                
                hr_response = service.users().dataset().aggregate(
                    userId='me',
                    body=hr_body
                ).execute()
                
                for bucket in hr_response.get('bucket', []):
                    start_ms = int(bucket.get('startTimeMillis', 0))
                    end_ms = int(bucket.get('endTimeMillis', 0))
                    
                    heart_rates = []
                    for point in bucket.get('point', []):
                        for value in point.get('value', []):
                            if 'fpVal' in value:
                                heart_rates.append(value['fpVal'])
                    
                    if heart_rates:
                        avg_hr = sum(heart_rates) / len(heart_rates)
                        start_dt = datetime.utcfromtimestamp(start_ms / 1000)
                        end_dt = datetime.utcfromtimestamp(end_ms / 1000)
                        
                        HealthDataPoint.objects.update_or_create(
                            dog=dog,
                            user=user,
                            source_type='heart_rate',
                            start_time=start_dt,
                            end_time=end_dt,
                            defaults={
                                'value': avg_hr,
                                'unit': 'bpm',
                                'data_source_name': 'Google Fit (heart rate)',
                            }
                        )
                        saved_count += 1
            
            except Exception:
                # Heart rate potrebbe non essere disponibile, ignora silenziosamente
                pass
                
        except Exception as e:
            errors.append(f"General error for {dog.dog_name}: {str(e)}")
            skipped += 1
    
    return {"saved": saved_count, "skipped": skipped, "errors": errors}


def sync_via_health_api(creds, user, dogs, days: int = 30) -> Dict[str, Any]:
    """
    Sincronizza usando Google Health Connect API (v1alpha, sperimentale).
    
    Note: Health API è ancora in anteprima, endpoint potrebbe cambiare.
    Attualmente restituisce placeholder.
    """
    # Nota: implementazione reale richiede ulteriori sviluppi
    # La API è in anteprima e la documentazione è in evoluzione
    
    from googleapiclient.discovery import build
    
    try:
        service = build('health', 'v1alpha', credentials=creds, static_discovery=False)
    except Exception as e:
        return {
            "saved": 0,
            "skipped": len(dogs),
            "errors": [f"Health API non disponibile: {str(e)}"]
        }
    
    saved_count = 0
    skipped = 0
    errors = []
    start_ns, end_ns = build_time_range(days)
    
    for dog in dogs:
        try:
            # Placeholder: implementare quando API stabile
            # endpoints: health.fitness.v1alpha.datasets.batchGet
            errors.append(f"Health API non implementata per {dog.dog_name}")
            skipped += 1
        except Exception as e:
            errors.append(f"Errore Health API per {dog.dog_name}: {str(e)}")
            skipped += 1
    
    return {"saved": saved_count, "skipped": skipped, "errors": errors}


def get_health_summary(user) -> Dict[str, Any]:
    """
    Restituisce riepilogo dati salute sincronizzati per utente.
    
    Args:
        user: Utente Django
        
    Returns:
        Dict con statistiche sintetiche
    """
    from canine_tools.models import HealthDataPoint
    
    summary = {
        'total_points': 0,
        'by_source': {},
        'latest_sync': None,
    }
    
    points = HealthDataPoint.objects.filter(user=user)
    summary['total_points'] = points.count()
    
    if points.exists():
        summary['latest_sync'] = points.latest('created_at').created_at
        
    for source, _ in HealthDataPoint.SOURCE_CHOICES:
        count = points.filter(source_type=source).count()
        summary['by_source'][source] = count
    
    return summary

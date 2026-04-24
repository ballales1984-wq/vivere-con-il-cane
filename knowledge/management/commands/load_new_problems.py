"""
Management command to load new knowledge problems (pk 11-20) without 
touching existing records, bypassing the auto_now_add=True constraint.
"""
from django.core.management.base import BaseCommand
from knowledge.models import Problem, Cause, Solution


NEW_PROBLEMS = [
    {"pk": 11, "title": "Reattività al guinzaglio", "slug": "reattivita-guinzaglio",
     "category": "behavior", "severity": "high",
     "description": "Il cane reagisce in modo esagerato ad altri cani, persone o biciclette durante le passeggiate: abbaia, tira, ringhia o salta. Non è aggressività vera ma un'emozione incontrollata amplificata dal guinzaglio.",
     "common_breeds": "Pastore Tedesco, Malinois, Border Collie, Levriero, Husky, Rottweiler"},
    {"pk": 12, "title": "Cane che mangia di tutto", "slug": "mangia-tutto-terra",
     "category": "health", "severity": "high",
     "description": "Il cane raccoglie e inghiotte oggetti da terra: sassi, fazzoletti, rifiuti, cibo altrui. Si chiama pica e può essere pericolosa per ostruzioni intestinali.",
     "common_breeds": "Labrador, Beagle, Bulldog, Border Collie, cuccioli in generale"},
    {"pk": 13, "title": "Paura degli estranei", "slug": "paura-estranei",
     "category": "behavior", "severity": "high",
     "description": "Il cane ha paura delle persone che non conosce: si nasconde, ringhia, abbaia o fugge. Nei casi gravi può mordere per autodifesa. Non è cattiveria ma paura.",
     "common_breeds": "Chihuahua, Pastore Tedesco, Pastore Belga, meticci con traumi"},
    {"pk": 14, "title": "Aggressività verso altri cani", "slug": "aggressivita-cani",
     "category": "behavior", "severity": "high",
     "description": "Il cane attacca o aggredisce altri cani: ringhia, abbaia in modo minaccioso, si lancia. Può succedere al guinzaglio o quando libero. È un problema serio che richiede attenzione immediata.",
     "common_breeds": "Pastore Tedesco, Malinois, Chow Chow, Akita, Rottweiler, Pit Bull"},
    {"pk": 15, "title": "Coprofagia (mangia le feci)", "slug": "mangia-feci",
     "category": "health", "severity": "medium",
     "description": "Il cane mangia le proprie feci o quelle di altri animali. Un comportamento disgustoso ma comune. Può avere cause nutrizionali, comportamentali o semplicemente istintive.",
     "common_breeds": "Labrador, Beagle, Yorkshire Terrier, cuccioli in generale"},
    {"pk": 16, "title": "Scava e distrugge il giardino", "slug": "scava-giardino",
     "category": "behavior", "severity": "low",
     "description": "Il cane scava buche nel giardino, distrugge aiuole e sradica piante. Può essere istinto, noia o un modo per cercare frescura o odori interessanti.",
     "common_breeds": "Terrier, Dachshund, Husky, Border Collie, Beagle, Labrador"},
    {"pk": 17, "title": "Paura del veterinario", "slug": "paura-veterinario",
     "category": "behavior", "severity": "medium",
     "description": "Il cane si agita, trema, cerca di scappare o aggredisce durante le visite veterinarie. Questo rende le visite stressanti per tutti e può portare a rinunciare a cure necessarie.",
     "common_breeds": "Tutte le razze, particolarmente comune in cani con esperienze negative pregresse"},
    {"pk": 18, "title": "Mal d'auto", "slug": "mal-auto",
     "category": "health", "severity": "low",
     "description": "Il cane sbava, vomita, si agita o ansima eccessivamente in macchina. Può essere nausea da movimento o ansia associata ai viaggi.",
     "common_breeds": "Tutte le razze, più comune nei cuccioli e in cani con poca esperienza di viaggio"},
    {"pk": 19, "title": "Si lecca ossessivamente le zampe", "slug": "lecca-zampe-ossessivo",
     "category": "health", "severity": "medium",
     "description": "Il cane si lecca continuamente le zampe, spesso fino a causare rossore, perdita di pelo o piaghe. Può essere allergia, dolore, noia o comportamento compulsivo.",
     "common_breeds": "Golden Retriever, Labrador, Bulldog Francese, West Highland Terrier"},
    {"pk": 20, "title": "Scarsa attenzione e difficoltà di concentrazione", "slug": "scarsa-attenzione",
     "category": "training", "severity": "low",
     "description": "Il cane si distrae facilmente durante il training o le passeggiate, ignora i comandi anche se li conosce, non riesce a mantenere il contatto visivo. Spesso scambiato per disobbedienza.",
     "common_breeds": "Beagle, Husky, Bassotto, Border Collie molto giovane, razze nordiche"},
]

NEW_CAUSES = [
    {"pk": 32, "problem_pk": 11, "description": "Frustrazione da guinzaglio - il cane vorrebbe avvicinarsi ma non può, la frustrazione esplode in reazione", "probability": "very_common", "notes": "Spesso in cani molto socievoli che non riescono a salutare"},
    {"pk": 33, "problem_pk": 11, "description": "Mancata socializzazione - il cane non è abituato ad altri cani o persone", "probability": "common", "notes": "Il periodo critico di socializzazione è 3-14 settimane"},
    {"pk": 34, "problem_pk": 12, "description": "Istinto di foraggiamento - alcuni cani hanno un impulso molto forte a cercare e ingerire cibo", "probability": "very_common", "notes": "Il Labrador è geneticamente predisposto a questa tendenza"},
    {"pk": 35, "problem_pk": 12, "description": "Noia e mancanza di stimoli - il cane esplora l'ambiente attraverso la bocca", "probability": "common", "notes": "Più frequente nei cani con poca stimolazione mentale"},
    {"pk": 36, "problem_pk": 13, "description": "Mancata socializzazione nel periodo critico - poca esposizione a persone diverse da cucciolo", "probability": "very_common", "notes": "Il periodo critico è tra 3 e 14 settimane di vita"},
    {"pk": 37, "problem_pk": 13, "description": "Esperienze traumatiche - il cane ha avuto interazioni negative con persone", "probability": "common", "notes": "Frequente in cani adottati con storia sconosciuta"},
    {"pk": 38, "problem_pk": 14, "description": "Mancata socializzazione canina - il cane non è abituato a interagire con altri cani", "probability": "very_common", "notes": "Fondamentale socializzare i cuccioli con tanti cani diversi"},
    {"pk": 39, "problem_pk": 14, "description": "Esperienza traumatica con un altro cane - un attacco passato crea paura e aggressività difensiva", "probability": "common", "notes": "Spesso è aggressività da paura, non dominanza"},
    {"pk": 40, "problem_pk": 15, "description": "Carenza nutrizionale - il cane cerca minerali o enzimi che non assume con la dieta", "probability": "common", "notes": "Valutare la qualità del cibo e aggiungere enzimi digestivi"},
    {"pk": 41, "problem_pk": 15, "description": "Comportamento istintivo - le femmine mangiano le feci dei cuccioli per tenere pulita la tana", "probability": "common", "notes": "Istinto naturale che può persistere in alcuni cani adulti"},
    {"pk": 42, "problem_pk": 16, "description": "Istinto naturale - molte razze sono state selezionate per scavare (terrier, tasso, lepre)", "probability": "very_common", "notes": "Non si può eliminare del tutto, va reindirizzato"},
    {"pk": 43, "problem_pk": 16, "description": "Noia - il cane non ha abbastanza stimoli e scava per passare il tempo", "probability": "common", "notes": "Aumentare esercizio fisico e mentale riduce drasticamente il problema"},
    {"pk": 44, "problem_pk": 17, "description": "Esperienze negative precedenti - visite dolorose o forzate hanno creato un'associazione negativa", "probability": "very_common", "notes": "Una sola esperienza traumatica è sufficiente per creare fobia"},
    {"pk": 45, "problem_pk": 17, "description": "Stimoli sensoriali - odori, rumori e manipolazione corporea sono disturbanti per il cane", "probability": "common", "notes": "L'odore del disinfettante è spesso il primo trigger"},
    {"pk": 46, "problem_pk": 18, "description": "Nausea da movimento - il sistema vestibolare del cane non è abituato al movimento del veicolo", "probability": "very_common", "notes": "Molto comune nei cuccioli, spesso migliora con l'età"},
    {"pk": 47, "problem_pk": 18, "description": "Ansia condizionata - la macchina è associata a esperienze negative (veterinario, abbandono)", "probability": "common", "notes": "Il cane anticipa qualcosa di brutto salendo in auto"},
    {"pk": 48, "problem_pk": 19, "description": "Allergie alimentari o ambientali - la pelle prude e il cane si lecca per alleviare il fastidio", "probability": "very_common", "notes": "Le allergie al polline, graminacee e cibo sono le cause più frequenti"},
    {"pk": 49, "problem_pk": 19, "description": "Comportamento compulsivo da stress o noia - leccarsi diventa un rituale ripetitivo", "probability": "common", "notes": "Simile ai comportamenti compulsivi umani (OCD)"},
    {"pk": 50, "problem_pk": 20, "description": "Ambiente troppo ricco di stimoli - il cane è sopraffatto da distrazioni e non riesce a concentrarsi", "probability": "very_common", "notes": "Iniziare sempre il training in ambienti silenziosi e privi di distrazioni"},
    {"pk": 51, "problem_pk": 20, "description": "Sessioni di training troppo lunghe - il cane si stanca mentalmente e perde l'interesse", "probability": "common", "notes": "Le sessioni ideali durano 3-5 minuti più volte al giorno, non 30 minuti di fila"},
]

NEW_SOLUTIONS = [
    {"pk": 28, "problem_pk": 11, "solution_type": "training", "title": "Tecnica 'guarda e vai'", "description": "Quando vedi il trigger da lontano, chiama il cane, fallo guardare verso il trigger, premialo e allontanati. Insegna che vedere un altro cane = cibo e allontanamento positivo.", "difficulty": "hard", "time_needed": "4-8 settimane", "success_rate": "high", "warnings": "Inizia sempre a distanza di sicurezza dal trigger, mai oltre la soglia di reazione"},
    {"pk": 29, "problem_pk": 11, "solution_type": "behavior", "title": "Aumenta la distanza di sicurezza", "description": "Non avvicinarti mai al trigger quando il cane è già reattivo. Attraversa la strada, cambia percorso. La gestione previene il rinforzo del comportamento.", "difficulty": "easy", "time_needed": "Immediato", "success_rate": "medium", "warnings": "La gestione non risolve il problema ma previene il peggioramento"},
    {"pk": 30, "problem_pk": 12, "solution_type": "training", "title": "Insegna 'lascia' e 'dammi'", "description": "Allena il comando 'lascia' con rinforzo positivo: offri un premio di alto valore in cambio dell'oggetto vietato. Mai inseguire il cane: lo rende un gioco.", "difficulty": "medium", "time_needed": "2-4 settimane", "success_rate": "high", "warnings": "Non punire fisicamente: può portare ad inghiottire l'oggetto ancora più velocemente"},
    {"pk": 31, "problem_pk": 12, "solution_type": "training", "title": "Museruola di sicurezza", "description": "Usa una museruola comoda tipo cestello nelle zone a rischio (parchi, strade). Non è una punizione ma uno strumento di sicurezza. Abituala con rinforzo positivo.", "difficulty": "easy", "time_needed": "1-2 settimane di abituazione", "success_rate": "high", "warnings": "La museruola non risolve il problema, gestiscilo in parallelo con il training"},
    {"pk": 32, "problem_pk": 13, "solution_type": "training", "title": "Desensibilizzazione graduale agli estranei", "description": "Chiedi agli estranei di ignorare completamente il cane. Lascia che sia lui ad avvicinarsi. Lancia premi sul pavimento vicino all'estraneo senza contatto diretto. Sessioni brevi e positive.", "difficulty": "hard", "time_needed": "4-12 settimane", "success_rate": "medium", "warnings": "Non forzare mai il contatto. La forza peggiora la paura e aumenta il rischio di morso"},
    {"pk": 33, "problem_pk": 14, "solution_type": "training", "title": "Consulto con educatore cinofilo esperto", "description": "L'aggressività inter-canina richiede una valutazione professionale. Un educatore qualificato può valutare il tipo di aggressività e creare un piano di lavoro sicuro e personalizzato.", "difficulty": "hard", "time_needed": "Variabile, 2-6 mesi", "success_rate": "medium", "warnings": "Non affrontare da soli casi di vera aggressività: il rischio di morsi è reale"},
    {"pk": 34, "problem_pk": 14, "solution_type": "environment", "title": "Gestione rigorosa degli spazi", "description": "Mantieni sempre il cane al guinzaglio in presenza di altri cani. Evita i parchi liberi. Usa la museruola nelle situazioni a rischio. Gestisci prima di rieducare.", "difficulty": "easy", "time_needed": "Immediato", "success_rate": "high", "warnings": "La gestione è fondamentale per la sicurezza, non è una soluzione a lungo termine"},
    {"pk": 35, "problem_pk": 15, "solution_type": "environment", "title": "Rimuovi le feci immediatamente", "description": "Porta a passeggio il cane con guinzaglio e raccogli subito le feci. In giardino, pulisci sempre entro pochi minuti. Rimuovi l'opportunità prima ancora che si crei.", "difficulty": "easy", "time_needed": "Immediato", "success_rate": "high", "warnings": "Serve costanza: basta una volta per reinforzare il comportamento"},
    {"pk": 36, "problem_pk": 15, "solution_type": "health", "title": "Integratori e cambio alimentazione", "description": "Parla con il veterinario di integratori di enzimi digestivi e probiotici. Un cambio a cibo di qualità superiore può ridurre il comportamento significativamente.", "difficulty": "easy", "time_needed": "2-4 settimane", "success_rate": "medium", "warnings": "Consulta sempre il veterinario prima di cambiare dieta o aggiungere integratori"},
    {"pk": 37, "problem_pk": 16, "solution_type": "environment", "title": "Zona di scavo autorizzata", "description": "Crea una zona dedicata allo scavo (sabbiera, angolo del giardino) e rendi quello spazio super interessante nascondendo giochi e premi. Reindirizza il cane lì ogni volta che scava altrove.", "difficulty": "easy", "time_needed": "2-4 settimane", "success_rate": "high", "warnings": "Non punire lo scavo ma reindirizzalo: è un bisogno naturale"},
    {"pk": 38, "problem_pk": 17, "solution_type": "training", "title": "Visite di familiarizzazione allo studio", "description": "Porta il cane in clinica solo per ricevere premi e andarsene, senza nessuna visita. Fallo spesso. Il cane impara che la clinica è un posto piacevole.", "difficulty": "easy", "time_needed": "4-8 settimane", "success_rate": "high", "warnings": "Scegli un veterinario 'fear-free' che collabori con questo approccio"},
    {"pk": 39, "problem_pk": 17, "solution_type": "behavior", "title": "Addestra la gestione corporea", "description": "Abitua il cane a essere toccato ovunque a casa tua: orecchie, denti, zampe, addome. Premia ogni manipolazione. Il veterinario non sarà più una sorpresa.", "difficulty": "easy", "time_needed": "2-4 settimane", "success_rate": "high", "warnings": "Inizia dalle zone dove il cane è meno sensibile, passa alle più delicate gradualmente"},
    {"pk": 40, "problem_pk": 18, "solution_type": "training", "title": "Desensibilizzazione graduale all'auto", "description": "Inizia dal far entrare il cane in auto ferma con premi. Poi accendi il motore. Poi fai giri di 2 minuti verso mete piacevoli (parco, non veterinario). Aumenta gradualmente.", "difficulty": "medium", "time_needed": "3-6 settimane", "success_rate": "high", "warnings": "Non fare subito viaggi lunghi. La progressione lenta è fondamentale"},
    {"pk": 41, "problem_pk": 18, "solution_type": "environment", "title": "Posizionamento e accessori", "description": "Metti il cane nel senso di marcia, possibilmente basso. Finestre aperte per arieggiare. Trasportino sicuro riduce l'ansia in molti cani.", "difficulty": "easy", "time_needed": "Immediato", "success_rate": "medium", "warnings": "Non dare cibo 2-3 ore prima del viaggio per ridurre la nausea"},
    {"pk": 42, "problem_pk": 19, "solution_type": "health", "title": "Visita veterinaria e test allergologici", "description": "Prima di tutto escludere cause fisiche: allergie alimentari (dieta ad eliminazione), dermatiti, funghi, dolore articolare. Solo dopo affrontare il lato comportamentale.", "difficulty": "medium", "time_needed": "4-8 settimane per i test", "success_rate": "high", "warnings": "Non mettere il collare elisabettiano senza capire la causa: risolve il sintomo non il problema"},
    {"pk": 43, "problem_pk": 20, "solution_type": "training", "title": "Allena il contatto visivo", "description": "Esercizio base: tieni un premio chiuso in mano, aspetta che il cane smetta di annusarla e ti guardi negli occhi, premia immediatamente. Ripeti fino a che non ti guarda spontaneamente.", "difficulty": "easy", "time_needed": "1-2 settimane", "success_rate": "high", "warnings": "Sessioni brevi (2-3 minuti), termina sempre con successo"},
    {"pk": 44, "problem_pk": 20, "solution_type": "training", "title": "Riduci le distrazioni gradualmente", "description": "Inizia ogni nuovo esercizio a casa, in silenzio. Poi in giardino. Poi in un parco vuoto. Poi in un parco frequentato. Aumenta la difficoltà dell'ambiente solo quando il comportamento è solido.", "difficulty": "medium", "time_needed": "4-8 settimane", "success_rate": "high", "warnings": "Non bruciare le tappe: se il cane fallisce, torna all'ambiente precedente"},
]


class Command(BaseCommand):
    help = "Load new knowledge problems (11-20) into the database"

    def handle(self, *args, **options):
        created_problems = 0
        created_causes = 0
        created_solutions = 0

        # Create problems
        for p_data in NEW_PROBLEMS:
            pk = p_data.pop("pk")
            obj, created = Problem.objects.get_or_create(
                pk=pk,
                defaults=p_data
            )
            if not created:
                # Update if slug doesn't match (fix any inconsistencies)
                for k, v in p_data.items():
                    setattr(obj, k, v)
                obj.save()
            else:
                created_problems += 1

        # Create causes
        for c_data in NEW_CAUSES:
            pk = c_data.pop("pk")
            problem_pk = c_data.pop("problem_pk")
            problem = Problem.objects.get(pk=problem_pk)
            obj, created = Cause.objects.get_or_create(
                pk=pk,
                defaults={"problem": problem, **c_data}
            )
            if created:
                created_causes += 1

        # Create solutions
        for s_data in NEW_SOLUTIONS:
            pk = s_data.pop("pk")
            problem_pk = s_data.pop("problem_pk")
            problem = Problem.objects.get(pk=problem_pk)
            obj, created = Solution.objects.get_or_create(
                pk=pk,
                defaults={"problem": problem, **s_data}
            )
            if created:
                created_solutions += 1

        self.stdout.write(self.style.SUCCESS(
            f"OK Creati: {created_problems} problemi, {created_causes} cause, {created_solutions} soluzioni."
        ))

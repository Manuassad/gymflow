"""Interface and alert text in English and French."""

ALERTS = {
    "en": {
        "HR_OVERLOAD": ("Heart rate overload", "{hr} bpm, above the {limit} bpm limit (85% of max HR).", "Reduce the load by 10% and rest longer."),
        "RPE_CRITICAL": ("Critical effort", "RPE {rpe}/10, close to muscular failure.", "Stop the set and rest at least 3 minutes."),
        "SHORT_REST": ("Short rest", "{rest}s of rest, below the {min_rest}s minimum.", "Wait at least {min_rest}s."),
        "FATIGUE": ("Fatigue", "{reps} of {target} planned reps at RPE {rpe}.", "Reduce the load by 5 to 10% on the next set."),
        "CAN_PROGRESS": ("Can progress", "Targets reached at RPE {rpe}.", "Suggest +2.5 kg on {exercise}."),
        "PLATEAU": ("Plateau", "No gain on {exercise} over the last 3 sessions.", "Change the volume or the exercise variation."),
    },
    "fr": {
        "HR_OVERLOAD": ("Surcharge cardiaque", "{hr} bpm, au-dessus de la limite de {limit} bpm (85 % de la FC max).", "Réduire la charge de 10 % et allonger le repos."),
        "RPE_CRITICAL": ("Effort critique", "RPE {rpe}/10, proche de l'échec musculaire.", "Arrêter la série et se reposer au moins 3 minutes."),
        "SHORT_REST": ("Repos court", "{rest} s de repos, sous le minimum de {min_rest} s.", "Attendre au moins {min_rest} s."),
        "FATIGUE": ("Fatigue", "{reps} répétitions sur {target} prévues à RPE {rpe}.", "Réduire la charge de 5 à 10 % à la prochaine série."),
        "CAN_PROGRESS": ("Progression possible", "Objectifs atteints à RPE {rpe}.", "Proposer +2,5 kg sur {exercise}."),
        "PLATEAU": ("Plateau", "Aucun gain sur {exercise} depuis 3 séances.", "Changer le volume ou la variante de l'exercice."),
    },
}

UI = {
    "en": {
        "tagline": "Real-time analysis of a simulated workout stream: three fictional athletes, one FIFO pipeline, one replayable event log.",
        "disclaimer": "All data is simulated. The rules are simple heuristics for a data engineering demo, not medical or training advice.",
        "settings": "Simulation", "sessions": "Sessions per athlete", "seed": "Random seed", "delay": "Delay between sets (ms)",
        "stop": "Graceful shutdown after N sets (0 = off)", "run": "Run simulation",
        "tab_live": "Session", "tab_alerts": "Alerts", "tab_arch": "How it works", "live_now": "Live feed",
        "m_sets": "Sets processed", "m_alerts": "Alerts raised", "m_lost": "Sets lost", "m_produced": "Sets produced", "m_latency": "Median in-process latency",
        "latency_note": "Latency runs from set creation to the end of processing. It says nothing about a real network or database unless the backends below are real.",
        "backend": "Backends: live view = {live}, event log = {log}.",
        "stopped": "Graceful shutdown triggered: every set that entered the queue was still processed.",
        "chart_alerts": "Alerts per athlete, by level", "chart_hr": "Heart rate by set", "chart_1rm": "Best estimated 1RM per session",
        "hr_limit": "Red alert limit", "set_order": "Set number in the session", "session": "Session", "hr": "Heart rate (bpm)", "e1rm": "Estimated 1RM (kg)", "count": "Alerts",
        "athlete": "Athlete", "exercise": "Exercise", "level": "Level", "alert": "Alert", "detail": "Detail", "action": "Recommended action", "set": "Set", "all": "All",
        "view_table": "Show the data as a table",
        "no_alerts": "No alerts for this selection.", "plateau_hint": "Plateau detection needs at least 3 sessions.",
        "arch_title": "Pipeline", "lock_title": "Why the per-athlete lock matters",
        "lock_text": "Concurrent coach edits on the same exercise are read-modify-write operations. This demo runs them with and without the lock.",
        "lock_run": "Run {n} concurrent edits of +1 kg", "with_lock": "With lock", "without_lock": "Without lock", "lock_result": "{applied:.0f} kg applied, {expected:.0f} kg expected",
        "replay_title": "Event log replay", "replay_text": "Each set is an event. These totals are rebuilt only by replaying the log.",
        "volume": "Volume (kg)", "sets": "Sets", "last_hr": "Last heart rate (bpm)",
        "levels": {"RED": "Red", "ORANGE": "Orange", "GREEN": "Green", "BLUE": "Blue"},
    },
    "fr": {
        "tagline": "Analyse en temps réel d'un flux de séances simulé : trois athlètes fictifs, un pipeline FIFO, un journal d'événements rejouable.",
        "disclaimer": "Toutes les données sont simulées. Les règles sont de simples heuristiques pour une démo de data engineering, pas un conseil médical ou sportif.",
        "settings": "Simulation", "sessions": "Séances par athlète", "seed": "Graine aléatoire", "delay": "Délai entre les séries (ms)",
        "stop": "Arrêt propre après N séries (0 = désactivé)", "run": "Lancer la simulation",
        "tab_live": "Séance", "tab_alerts": "Alertes", "tab_arch": "Fonctionnement", "live_now": "Flux en direct",
        "m_sets": "Séries traitées", "m_alerts": "Alertes levées", "m_lost": "Séries perdues", "m_produced": "Séries produites", "m_latency": "Latence médiane interne",
        "latency_note": "La latence va de la création de la série à la fin de son traitement. Elle ne dit rien d'un vrai réseau ou d'une vraie base, sauf si les bases ci-dessous sont réelles.",
        "backend": "Bases : vue en direct = {live}, journal d'événements = {log}.",
        "stopped": "Arrêt propre déclenché : toutes les séries entrées dans la file ont quand même été traitées.",
        "chart_alerts": "Alertes par athlète et par niveau", "chart_hr": "Fréquence cardiaque par série", "chart_1rm": "Meilleur 1RM estimé par séance",
        "hr_limit": "Limite de l'alerte rouge", "set_order": "Numéro de la série dans la séance", "session": "Séance", "hr": "Fréquence cardiaque (bpm)", "e1rm": "1RM estimé (kg)", "count": "Alertes",
        "athlete": "Athlète", "exercise": "Exercice", "level": "Niveau", "alert": "Alerte", "detail": "Détail", "action": "Action recommandée", "set": "Série", "all": "Tous",
        "view_table": "Afficher les données en tableau",
        "no_alerts": "Aucune alerte pour cette sélection.", "plateau_hint": "La détection de plateau demande au moins 3 séances.",
        "arch_title": "Pipeline", "lock_title": "À quoi sert le verrou par athlète",
        "lock_text": "Les modifications simultanées d'un même exercice par les coachs sont des opérations lecture-modification-écriture. Cette démo les exécute avec et sans verrou.",
        "lock_run": "Lancer {n} modifications simultanées de +1 kg", "with_lock": "Avec verrou", "without_lock": "Sans verrou", "lock_result": "{applied:.0f} kg appliqués, {expected:.0f} kg attendus",
        "replay_title": "Relecture du journal", "replay_text": "Chaque série est un événement. Ces totaux sont recalculés uniquement en rejouant le journal.",
        "volume": "Volume (kg)", "sets": "Séries", "last_hr": "Dernière fréquence cardiaque (bpm)",
        "levels": {"RED": "Rouge", "ORANGE": "Orange", "GREEN": "Vert", "BLUE": "Bleu"},
    },
}


def describe_alert(alert, lang="en"):
    """Return the (title, detail, action) text of an alert."""
    title, detail, action = ALERTS[lang][alert["type"]]
    params = alert["params"]
    return title, detail.format(**params), action.format(**params)

"""Business rules: pure functions, so they can be tested without any stream or database.

The thresholds are simple training heuristics. GymFlow is a data engineering demo, not medical advice.
"""

HR_OVERLOAD_RATIO = 0.85
RPE_CRITICAL = 9
HEAVY_LOAD_RATIO = 0.70
PLATEAU_SESSIONS = 3
PLATEAU_MIN_GAIN = 0.01


def epley_1rm(weight: float, reps: int) -> float:
    """Estimated one-rep max (Epley formula)."""
    return weight * (1 + reps / 30)


def analyse_set(s: dict) -> list[dict]:
    """Return the alerts raised by one set. Alerts hold data only; i18n.py turns them into text."""
    alerts = []
    hr_limit = int(s["max_hr"] * HR_OVERLOAD_RATIO)
    if s["hr"] > hr_limit:
        alerts.append({"level": "RED", "type": "HR_OVERLOAD", "params": {"hr": s["hr"], "limit": hr_limit}})
    if s["rpe"] >= RPE_CRITICAL:
        alerts.append({"level": "RED", "type": "RPE_CRITICAL", "params": {"rpe": s["rpe"]}})
    # The load is compared to the 1RM estimated for this exercise, not to the bench press 1RM.
    heavy = s["weight"] > HEAVY_LOAD_RATIO * epley_1rm(s["target_weight"], s["target_reps"])
    if s["rest"] < s["min_rest"] and heavy:
        alerts.append({"level": "ORANGE", "type": "SHORT_REST", "params": {"rest": s["rest"], "min_rest": s["min_rest"]}})
    if s["reps"] < s["target_reps"] and s["rpe"] > 7:
        alerts.append({"level": "ORANGE", "type": "FATIGUE",
                       "params": {"reps": s["reps"], "target": s["target_reps"], "rpe": s["rpe"]}})
    if s["reps"] >= s["target_reps"] and s["rpe"] <= 6:
        alerts.append({"level": "GREEN", "type": "CAN_PROGRESS", "params": {"rpe": s["rpe"], "exercise": s["exercise"]}})
    return alerts


def is_plateau(best_1rm_by_session: list[float]) -> bool:
    """Plateau: over the last PLATEAU_SESSIONS sessions, the estimated 1RM gained less than PLATEAU_MIN_GAIN."""
    if len(best_1rm_by_session) < PLATEAU_SESSIONS:
        return False
    window = best_1rm_by_session[-PLATEAU_SESSIONS:]
    return window[-1] <= window[0] * (1 + PLATEAU_MIN_GAIN)

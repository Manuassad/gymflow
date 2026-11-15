"""Fictional athletes and training programmes used by the simulator.

Every value is a simulation assumption, not a measurement of a real person.
"""

ATHLETES = {
    "ALEX": {"level": "intermediate", "max_hr": 194, "rest_hr": 68,
             "tendency": "overreaching", "mean_rpe": 8.2, "hr_factor": 0.82},
    "SARA": {"level": "beginner", "max_hr": 197, "rest_hr": 74,
             "tendency": "progressing", "mean_rpe": 6.5, "hr_factor": 0.68},
    "MALIK": {"level": "advanced", "max_hr": 190, "rest_hr": 58,
              "tendency": "plateau", "mean_rpe": 7.0, "hr_factor": 0.72},
}

PROGRAMME = {
    "ALEX": [
        {"exercise": "Bench Press", "sets": 4, "reps": 8, "weight": 72.0, "rpe": 7, "min_rest": 120},
        {"exercise": "Shoulder Press", "sets": 3, "reps": 10, "weight": 50.0, "rpe": 6, "min_rest": 90},
        {"exercise": "Triceps", "sets": 3, "reps": 12, "weight": 30.0, "rpe": 6, "min_rest": 60},
    ],
    "SARA": [
        {"exercise": "Bench Press", "sets": 3, "reps": 10, "weight": 22.0, "rpe": 6, "min_rest": 90},
        {"exercise": "Shoulder Press", "sets": 3, "reps": 12, "weight": 14.0, "rpe": 5, "min_rest": 60},
        {"exercise": "Triceps", "sets": 2, "reps": 15, "weight": 10.0, "rpe": 5, "min_rest": 60},
    ],
    "MALIK": [
        {"exercise": "Bench Press", "sets": 5, "reps": 5, "weight": 120.0, "rpe": 8, "min_rest": 180},
        {"exercise": "Shoulder Press", "sets": 4, "reps": 8, "weight": 80.0, "rpe": 7, "min_rest": 120},
        {"exercise": "Triceps", "sets": 3, "reps": 10, "weight": 45.0, "rpe": 7, "min_rest": 90},
    ],
}


def sets_per_session() -> int:
    return sum(ex["sets"] for programme in PROGRAMME.values() for ex in programme)

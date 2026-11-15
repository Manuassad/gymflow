"""Synthetic set stream, standing in for a connected watch or sensor."""
import asyncio
import random
import time

from gymflow.concurrency import ProgramStore
from gymflow.profiles import ATHLETES

PROGRESSION_PER_SESSION = 0.03


def _simulate_set(rng, profile, exercise, set_number, target_weight):
    tendency = profile["tendency"]
    base_hr = profile["max_hr"] * profile["hr_factor"] * (1 + (set_number - 1) * 0.05)

    if tendency == "overreaching":
        hr = rng.gauss(base_hr * 1.08, 8)
        rpe = rng.gauss(profile["mean_rpe"] + 0.5, 0.8)
        weight = target_weight + rng.choice([0, 2.5, 5])
        rest = exercise["min_rest"] - rng.randint(20, 50)
    elif tendency == "plateau":
        hr = rng.gauss(base_hr * 0.95, 5)
        rpe = rng.gauss(profile["mean_rpe"], 0.5)
        weight = target_weight
        rest = exercise["min_rest"] + rng.randint(0, 30)
    else:
        hr = rng.gauss(base_hr, 6)
        rpe = rng.gauss(profile["mean_rpe"] - 0.3, 0.7)
        weight = target_weight - rng.choice([0, 0, 2.5])
        rest = exercise["min_rest"] + rng.randint(0, 30)

    rpe = round(min(10, max(1, rpe)), 1)
    if rpe >= 9:
        reps = max(1, exercise["reps"] - rng.randint(2, 3))
    elif rpe <= 6:
        reps = exercise["reps"] + rng.choice([0, 1])
    else:
        reps = exercise["reps"] + rng.choice([-1, 0, 0, 1])

    return {"hr": max(profile["rest_hr"], min(int(hr), profile["max_hr"])),
            "rpe": rpe, "weight": weight, "reps": reps, "rest": rest}


async def athlete_stream(athlete, session, seed, programs: ProgramStore, delay=0.0):
    """Yield the sets of one session. Each athlete has its own RNG, so results do not depend on task timing."""
    rng = random.Random(f"{seed}:{athlete}:{session}")
    profile = ATHLETES[athlete]
    for exercise in programs.programme(athlete):
        target = programs.target(athlete, exercise["exercise"])
        if profile["tendency"] == "progressing":
            target = round(target * (1 + PROGRESSION_PER_SESSION * session) * 2) / 2
        for set_number in range(1, exercise["sets"] + 1):
            yield {
                "session": session, "athlete": athlete, "level": profile["level"],
                "max_hr": profile["max_hr"], "exercise": exercise["exercise"],
                "set": set_number, "planned_sets": exercise["sets"],
                "target_weight": target, "target_reps": exercise["reps"], "target_rpe": exercise["rpe"],
                "min_rest": exercise["min_rest"],
                **_simulate_set(rng, profile, exercise, set_number, target),
                "created_at": time.perf_counter(),
            }
            await asyncio.sleep(delay * rng.uniform(0.5, 1.5))

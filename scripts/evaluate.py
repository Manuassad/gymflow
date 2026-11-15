"""Sanity check of the rules over many seeds: python scripts/evaluate.py --seeds 200 --sessions 5

The data is simulated and the profiles were written with these rules in mind. This verifies that the pipeline
behaves as designed. It is not a measure of real-world accuracy.
"""
import argparse
import asyncio
import sys
import uuid
from collections import Counter
from pathlib import Path

import mongomock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gymflow.engine import run_block  # noqa: E402
from gymflow.profiles import ATHLETES  # noqa: E402
from gymflow.storage import EventLog, MemoryLiveStore  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=200)
    parser.add_argument("--sessions", type=int, default=5)
    args = parser.parse_args()

    sets, alerts, lost = Counter(), Counter(), 0
    eligible = Counter()
    for seed in range(args.seeds):
        log = EventLog(mongomock.MongoClient()[f"eval_{uuid.uuid4().hex}"])
        result = asyncio.run(run_block(args.sessions, seed, log=log, live=MemoryLiveStore()))
        lost += result["stats"]["produced"] - result["stats"]["persisted"]
        for s in result["sets"]:
            sets[s["athlete"]] += 1
            if s["session"] >= 2 and s["set"] == s["planned_sets"]:
                eligible[s["athlete"]] += 1
        for a in result["alerts"]:
            alerts[a["athlete"], a["level"]] += 1

    print(f"{args.seeds} seeds, {args.sessions} sessions per seed, {sum(sets.values())} sets, {lost} lost")
    print("| Athlete | Tendency | Red alerts per set | Orange alerts per set | Green alerts per set | Plateau alerts per check |")
    print("|---|---|---|---|---|---|")
    for athlete, profile in ATHLETES.items():
        n = sets[athlete]
        print(f"| {athlete} | {profile['tendency']} | {alerts[athlete, 'RED'] / n:.2f} | {alerts[athlete, 'ORANGE'] / n:.2f} "
              f"| {alerts[athlete, 'GREEN'] / n:.2f} | {alerts[athlete, 'BLUE'] / eligible[athlete]:.2f} |")


if __name__ == "__main__":
    main()

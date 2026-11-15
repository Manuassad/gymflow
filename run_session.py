"""Command line entry point: python run_session.py --sessions 3 --seed 42"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gymflow.engine import run_block  # noqa: E402
from gymflow.i18n import describe_alert  # noqa: E402


def print_set(s, alerts):
    print(f"[session {s['session'] + 1}] {s['athlete']:<5} {s['exercise']:<14} set {s['set']}/{s['planned_sets']}  "
          f"{s['weight']:>5} kg x {s['reps']:<2}  HR {s['hr']:>3}  RPE {s['rpe']:>4}  rest {s['rest']:>3}s")
    for alert in alerts:
        title, detail, action = describe_alert(alert)
        print(f"    {alert['level']:<6} {title}: {detail} -> {action}")


def main():
    parser = argparse.ArgumentParser(description="Run the GymFlow simulation.")
    parser.add_argument("--sessions", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--delay", type=float, default=0.2, help="average delay between sets, in seconds")
    parser.add_argument("--stop-after", type=int, default=None, help="trigger a graceful shutdown after N sets")
    args = parser.parse_args()
    result = asyncio.run(run_block(args.sessions, args.seed, args.delay, args.stop_after, on_set=print_set))
    print(result["stats"])


if __name__ == "__main__":
    main()

"""Stream consumer and session orchestration."""
import asyncio
import statistics
import time

from gymflow.concurrency import END_OF_STREAM, ProgramStore, ShutdownSignal, produce
from gymflow.profiles import ATHLETES
from gymflow.rules import analyse_set, epley_1rm, is_plateau
from gymflow.simulator import athlete_stream
from gymflow.storage import event_log_from_env, live_store_from_env


def rebuild_state(events):
    """Event sourcing: rebuild each athlete's training totals by replaying the log."""
    state = {}
    for e in sorted(events, key=lambda e: e["seq"]):
        s = state.setdefault(e["athlete"], {"sets": 0, "volume_kg": 0.0, "last_hr": None})
        s["sets"] += 1
        s["volume_kg"] += e["weight"] * e["reps"]
        s["last_hr"] = e["hr"]
    return state


def _check_plateau(event, log):
    """Only on the last set of an exercise, so that it raises at most one alert per session."""
    if event["set"] != event["planned_sets"]:
        return []
    best = {}
    for e in log.exercise_history(event["athlete"], event["exercise"]):
        best[e["session"]] = max(best.get(e["session"], 0), epley_1rm(e["weight"], e["reps"]))
    history = [best[session] for session in sorted(best)]
    if not is_plateau(history):
        return []
    return [{"level": "BLUE", "type": "PLATEAU", "params": {"exercise": event["exercise"]}}]


async def consume(queue, producers, log, live, stats, on_set=None, on_processed=None):
    """FIFO consumer. It stops only when every producer has finished, so queued sets are never dropped."""
    finished = 0
    while finished < producers:
        item = await queue.get()
        if item is END_OF_STREAM:
            finished += 1
            continue
        created_at = item.pop("created_at")
        item["seq"] = stats["persisted"]
        await asyncio.to_thread(log.append_set, item)
        alerts = analyse_set(item) + await asyncio.to_thread(_check_plateau, item, log)
        await asyncio.to_thread(log.append_alerts, [
            {**alert, "athlete": item["athlete"], "session": item["session"], "exercise": item["exercise"], "set": item["set"]}
            for alert in alerts])
        await asyncio.to_thread(live.set_live, item["athlete"], {k: item[k] for k in ("exercise", "set", "hr", "rpe", "weight")})
        stats["persisted"] += 1
        stats["alerts"] += len(alerts)
        stats["latencies_ms"].append((time.perf_counter() - created_at) * 1000)
        if on_set:
            on_set(item, alerts)
        if on_processed:
            on_processed(stats)


async def run_block(sessions=1, seed=42, delay=0.0, stop_after=None, on_set=None, log=None, live=None):
    """Run consecutive sessions for all athletes. `stop_after` triggers a graceful shutdown after N processed sets."""
    log = log or event_log_from_env()
    live = live or live_store_from_env()
    programs, shutdown = ProgramStore(), ShutdownSignal()
    stats = {"produced": 0, "persisted": 0, "alerts": 0, "latencies_ms": [], "stopped_early": False}

    def stop_if_needed(current):
        if stop_after is not None and current["persisted"] >= stop_after and not shutdown.is_set():
            current["stopped_early"] = True
            shutdown.set()

    for session in range(sessions):
        if shutdown.is_set():
            break
        queue = asyncio.Queue()
        producers = [produce(athlete_stream(athlete, session, seed, programs, delay), queue, shutdown, stats)
                     for athlete in ATHLETES]
        await asyncio.gather(*producers, consume(queue, len(producers), log, live, stats, on_set, stop_if_needed))

    latencies = stats.pop("latencies_ms")
    stats["latency_median_ms"] = statistics.median(latencies) if latencies else None
    return {"stats": stats, "sets": log.all_sets(), "alerts": log.all_alerts(),
            "live_backend": live.name, "log_backend": log.name}

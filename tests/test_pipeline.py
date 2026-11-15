import asyncio
import uuid

import mongomock
import pytest

from gymflow.concurrency import concurrent_edits_demo
from gymflow.engine import rebuild_state, run_block
from gymflow.i18n import ALERTS, UI, describe_alert
from gymflow.profiles import sets_per_session
from gymflow.storage import EventLog, MemoryLiveStore


def run(**kwargs):
    log = EventLog(mongomock.MongoClient()[f"test_{uuid.uuid4().hex}"])
    live = MemoryLiveStore()
    return asyncio.run(run_block(log=log, live=live, **kwargs)), live


def test_full_session_processes_every_set():
    result, _ = run()
    assert result["stats"]["produced"] == result["stats"]["persisted"] == sets_per_session() == 30
    assert len(result["sets"]) == 30


def test_same_seed_gives_same_results():
    first, _ = run(seed=7, sessions=2)
    second, _ = run(seed=7, sessions=2)

    def rows(result):
        key = ("session", "athlete", "exercise", "set", "hr", "rpe", "weight", "reps", "rest")
        return sorted(tuple(s[k] for k in key) for s in result["sets"])

    assert rows(first) == rows(second)
    assert first["stats"]["alerts"] == second["stats"]["alerts"]


def test_different_seeds_differ():
    first, _ = run(seed=1)
    second, _ = run(seed=2)
    assert [s["hr"] for s in first["sets"]] != [s["hr"] for s in second["sets"]]


@pytest.mark.parametrize("stop_after", [1, 5, 17, 29])
def test_graceful_shutdown_loses_nothing_and_does_not_hang(stop_after):
    result, _ = run(stop_after=stop_after, sessions=3, delay=0.001)
    stats = result["stats"]
    assert stats["stopped_early"]
    assert stats["produced"] == stats["persisted"] == len(result["sets"])
    assert stop_after <= stats["persisted"] < 90


def test_event_log_replay_matches_a_direct_total():
    result, _ = run(sessions=2)
    state = rebuild_state(result["sets"])
    assert sum(s["sets"] for s in state.values()) == len(result["sets"])
    for athlete, s in state.items():
        expected = sum(e["weight"] * e["reps"] for e in result["sets"] if e["athlete"] == athlete)
        assert s["volume_kg"] == pytest.approx(expected)


def test_live_store_keeps_the_latest_set():
    result, live = run()
    for athlete in ("ALEX", "SARA", "MALIK"):
        last = max((s for s in result["sets"] if s["athlete"] == athlete), key=lambda s: s["seq"])
        assert live.get_live(athlete)["hr"] == last["hr"]


def test_plateau_needs_three_sessions():
    two, _ = run(sessions=2)
    assert not [a for a in two["alerts"] if a["type"] == "PLATEAU"]
    five, _ = run(sessions=5)
    assert [a for a in five["alerts"] if a["type"] == "PLATEAU" and a["athlete"] == "MALIK"]


def test_lock_prevents_lost_updates():
    with_lock = asyncio.run(concurrent_edits_demo(use_lock=True))
    without_lock = asyncio.run(concurrent_edits_demo(use_lock=False))
    assert with_lock["applied"] == with_lock["expected"] == 20
    assert without_lock["applied"] < without_lock["expected"]


def test_every_alert_has_text_in_both_languages():
    assert ALERTS["en"].keys() == ALERTS["fr"].keys()
    assert UI["en"].keys() == UI["fr"].keys()
    alert = {"type": "PLATEAU", "params": {"exercise": "Triceps"}}
    assert "Triceps" in describe_alert(alert, "fr")[1]

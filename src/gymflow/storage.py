"""Polyglot persistence: a key-value store for the live view, a document store for the event log.

Without environment variables everything runs in memory, so no account or secret is needed.
"""
import json
import os
import uuid

import mongomock
from pymongo import MongoClient

LIVE_TTL_SECONDS = 300


class MemoryLiveStore:
    """In-memory stand-in for Redis."""
    name = "in-memory"

    def __init__(self):
        self.data = {}

    def set_live(self, athlete, state):
        self.data[athlete] = state

    def get_live(self, athlete):
        return self.data.get(athlete)


class RedisLiveStore:
    """Current state of each athlete in Upstash Redis, expired automatically after the session."""
    name = "Redis"

    def __init__(self, url, token):
        from upstash_redis import Redis
        self.client = Redis(url=url, token=token)

    def set_live(self, athlete, state):
        self.client.set(f"gymflow:live:{athlete}", json.dumps(state), ex=LIVE_TTL_SECONDS)

    def get_live(self, athlete):
        value = self.client.get(f"gymflow:live:{athlete}")
        return json.loads(value) if value else None


class EventLog:
    """Append-only log of sets and alerts. `run_id` isolates each simulation inside a shared database."""

    def __init__(self, database, run_id=None, name="in-memory"):
        self.run_id = run_id or uuid.uuid4().hex
        self.name = name
        self.sets = database["sets"]
        self.alerts = database["alerts"]

    def append_set(self, event):
        self.sets.insert_one({**event, "run_id": self.run_id})

    def append_alerts(self, alerts):
        if alerts:
            self.alerts.insert_many([{**alert, "run_id": self.run_id} for alert in alerts])

    def all_sets(self):
        return list(self.sets.find({"run_id": self.run_id}, {"_id": 0}))

    def all_alerts(self):
        return list(self.alerts.find({"run_id": self.run_id}, {"_id": 0}))

    def exercise_history(self, athlete, exercise):
        return list(self.sets.find({"run_id": self.run_id, "athlete": athlete, "exercise": exercise}, {"_id": 0}))


def live_store_from_env():
    url, token = os.environ.get("REDIS_URL"), os.environ.get("REDIS_TOKEN")
    return RedisLiveStore(url, token) if url and token else MemoryLiveStore()


def event_log_from_env():
    uri = os.environ.get("MONGO_URI")
    if uri:
        return EventLog(MongoClient(uri, serverSelectionTimeoutMS=5000)["gymflow"], name="MongoDB")
    return EventLog(mongomock.MongoClient()[f"gymflow_{uuid.uuid4().hex}"])

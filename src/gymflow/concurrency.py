"""Concurrency patterns: FIFO fan-in queue, graceful shutdown and per-athlete locks."""
import asyncio
import copy
import threading

from gymflow.profiles import PROGRAMME

END_OF_STREAM = object()


class ShutdownSignal:
    """Stop signal that can be raised from another thread (a UI, an OS signal handler) or from the event loop."""

    def __init__(self):
        self._flag = threading.Event()

    def set(self):
        self._flag.set()

    def is_set(self):
        return self._flag.is_set()


async def produce(stream, queue: asyncio.Queue, shutdown: ShutdownSignal, stats: dict):
    """Fan-in producer. On shutdown it stops reading and always tells the consumer that it has finished."""
    try:
        async for item in stream:
            if shutdown.is_set():
                break
            await queue.put(item)
            stats["produced"] += 1
    finally:
        await stream.aclose()
        await queue.put(END_OF_STREAM)


class ProgramStore:
    """Coach-editable programme. A per-athlete lock serialises read-modify-write edits."""

    def __init__(self):
        self._programmes = copy.deepcopy(PROGRAMME)
        self._locks = {athlete: asyncio.Lock() for athlete in self._programmes}

    def programme(self, athlete):
        return self._programmes[athlete]

    def _exercise(self, athlete, exercise):
        return next(ex for ex in self._programmes[athlete] if ex["exercise"] == exercise)

    def target(self, athlete, exercise):
        return self._exercise(athlete, exercise)["weight"]

    async def _edit(self, athlete, exercise, delta):
        current = self.target(athlete, exercise)
        await asyncio.sleep(0)  # stands in for the network round trip of a real read-modify-write
        self._exercise(athlete, exercise)["weight"] = current + delta

    async def adjust(self, athlete, exercise, delta, use_lock=True):
        if use_lock:
            async with self._locks[athlete]:
                await self._edit(athlete, exercise, delta)
        else:
            await self._edit(athlete, exercise, delta)


async def concurrent_edits_demo(edits=20, delta=1.0, use_lock=True):
    """Apply `edits` concurrent coach edits and return the weight change expected and the one really applied."""
    store = ProgramStore()
    before = store.target("ALEX", "Bench Press")
    await asyncio.gather(*(store.adjust("ALEX", "Bench Press", delta, use_lock) for _ in range(edits)))
    return {"expected": edits * delta, "applied": store.target("ALEX", "Bench Press") - before}

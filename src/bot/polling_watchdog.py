"""Polling liveness: heartbeat log line + exit when getUpdates stops succeeding.

PTB's polling task can end (or hang) after network errors while the process and
``Updater.running`` still look healthy. Nothing is logged then, so the bot is
deaf for hours. This module records every successful getUpdates round trip and
exits the process when none arrived for ``stall_seconds`` so PM2 restarts it.
"""

import asyncio
import os
import time
from typing import Any, Callable, Optional

import structlog
from telegram.request import HTTPXRequest

logger = structlog.get_logger(__name__)

HEARTBEAT_INTERVAL_SECONDS = 30 * 60
CHECK_INTERVAL_SECONDS = 30
# A healthy long poll returns every ~10 s; PTB retries errors with <=30 s backoff.
STALL_SECONDS = 300
EXIT_CODE = 3


class PollingLiveness:
    """Monotonic timestamp of the last successful getUpdates call."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self.last_success = clock()

    def mark_success(self) -> None:
        self.last_success = self._clock()

    def idle_seconds(self) -> float:
        return self._clock() - self.last_success


class LivenessRequest(HTTPXRequest):
    """HTTPXRequest that marks liveness after each successful getUpdates."""

    def __init__(self, liveness: PollingLiveness, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._liveness = liveness

    async def post(self, url: str, *args: Any, **kwargs: Any) -> Any:
        result = await super().post(url, *args, **kwargs)
        if url.endswith("/getUpdates"):
            self._liveness.mark_success()
        return result


def _hard_exit(code: int) -> None:
    # os._exit: the event loop may be wedged, a graceful shutdown could hang.
    os._exit(code)


async def watch_polling(
    liveness: PollingLiveness,
    *,
    stall_seconds: float = STALL_SECONDS,
    heartbeat_seconds: float = HEARTBEAT_INTERVAL_SECONDS,
    check_seconds: float = CHECK_INTERVAL_SECONDS,
    exit_fn: Callable[[int], Any] = _hard_exit,
    clock: Callable[[], float] = time.monotonic,
    polling_task_done: Optional[Callable[[], bool]] = None,
) -> None:
    """Log a heartbeat and exit the process when polling stalls."""
    next_heartbeat = clock() + heartbeat_seconds
    while True:
        await asyncio.sleep(check_seconds)
        idle = liveness.idle_seconds()
        task_dead = bool(polling_task_done and polling_task_done())
        if idle > stall_seconds or task_dead:
            logger.error(
                "polling.stalled",
                idle_seconds=round(idle),
                polling_task_done=task_dead,
            )
            exit_fn(EXIT_CODE)
            return
        if clock() >= next_heartbeat:
            logger.info("polling.heartbeat", last_update_seconds_ago=round(idle))
            next_heartbeat = clock() + heartbeat_seconds

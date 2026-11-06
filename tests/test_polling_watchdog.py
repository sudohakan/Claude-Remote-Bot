"""Polling watchdog: heartbeat log and exit on stalled getUpdates."""

import asyncio

from src.bot.polling_watchdog import PollingLiveness, watch_polling


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


async def _run(clock, liveness, steps, **kw):
    exits: list[int] = []

    async def fast_sleep(_):
        clock.now += 30
        steps.pop(0)() if steps else None

    real_sleep = asyncio.sleep
    asyncio.sleep = fast_sleep
    try:
        await asyncio.wait_for(
            watch_polling(
                liveness, exit_fn=exits.append, clock=clock, check_seconds=30, **kw
            ),
            timeout=2,
        )
    finally:
        asyncio.sleep = real_sleep
    return exits


async def test_exits_when_no_successful_poll():
    clock = FakeClock()
    liveness = PollingLiveness(clock)
    exits = await _run(clock, liveness, [], stall_seconds=300)
    assert exits == [3]


async def test_exits_when_polling_task_dead():
    clock = FakeClock()
    liveness = PollingLiveness(clock)
    exits = await _run(
        clock, liveness, [], stall_seconds=10_000, polling_task_done=lambda: True
    )
    assert exits == [3]


async def test_heartbeat_logged_while_healthy(capsys):
    clock = FakeClock()
    liveness = PollingLiveness(clock)
    steps = [liveness.mark_success] * 5 + [
        lambda: setattr(clock, "now", clock.now + 999)
    ]
    exits = await _run(clock, liveness, steps, stall_seconds=300, heartbeat_seconds=120)
    assert exits == [3]
    assert "polling.heartbeat" in capsys.readouterr().out

from unittest.mock import AsyncMock, patch

import pytest
from telegram.error import NetworkError, TimedOut

from src.bot import orchestrator as orch


async def test_retries_then_succeeds():
    bot = AsyncMock()
    bot.set_my_commands.side_effect = [TimedOut("t"), NetworkError("n"), None]
    with patch.object(orch.asyncio, "sleep", new=AsyncMock()) as sleep:
        assert await orch._set_commands_with_retry(bot, [], None) is True
    assert bot.set_my_commands.await_count == 3
    assert [c.args[0] for c in sleep.await_args_list] == [2.0, 4.0]


async def test_gives_up_without_raising():
    bot = AsyncMock()
    bot.set_my_commands.side_effect = TimedOut("t")
    with patch.object(orch.asyncio, "sleep", new=AsyncMock()):
        assert await orch._set_commands_with_retry(bot, [], None) is False
    assert bot.set_my_commands.await_count == orch.COMMANDS_RETRY_ATTEMPTS


async def test_other_errors_propagate():
    bot = AsyncMock()
    bot.set_my_commands.side_effect = ValueError("bad")
    with pytest.raises(ValueError):
        await orch._set_commands_with_retry(bot, [], None)

import asyncio
import logging
from typing import List, Optional, Tuple

from mrlazy_bot.local_poller.allowlist import AllowedCommand
from mrlazy_bot.models import CommandExecutionResult, CommandExecutionError


logger = logging.getLogger(__name__)

async def run_allowed_command_async(
    allowed: AllowedCommand,
    runtime_args: List[str],
) -> Tuple[int, str, str]:
    """
    Async variant using asyncio subprocess APIs so command execution does not block the event loop.
    """
    argv = [allowed.exec] + list(allowed.fixed_args or []) + list(runtime_args or [])
    timeout = allowed.timeout
    process = await asyncio.create_subprocess_exec(
        *argv,
        cwd=allowed.working_dir or None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout_b, stderr_b = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError as e:
        logger.error(f"Command '{allowed.exec}' timed out after {timeout}s")
        process.kill()
        await process.communicate()
        raise e

    result = CommandExecutionResult(exit_code=process.returncode, stdout=stdout_b, stderr=stderr_b)
    result.raise_for_status()

    return result


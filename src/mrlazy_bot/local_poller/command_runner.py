import subprocess
from typing import List, Optional, Tuple

from mrlazy_bot.local_poller.allowlist import AllowedCommand


class CommandExecutionError(Exception):
    pass


def run_allowed_command(
    allowed: AllowedCommand,
    runtime_args: List[str],
    default_timeout: int,
) -> Tuple[int, str, str]:
    argv = [allowed.exec] + list(allowed.fixed_args or []) + list(runtime_args or [])
    timeout = allowed.timeout or default_timeout
    try:
        proc = subprocess.run(
            argv,
            cwd=allowed.working_dir or None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired as e:
        raise CommandExecutionError(f"Timeout after {timeout}s") from e
    except FileNotFoundError as e:
        raise CommandExecutionError(f"Executable not found: {allowed.exec}") from e


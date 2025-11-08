from mrlazy_bot.local_poller.allowlist import AllowedCommand
from mrlazy_bot.local_poller.command_runner import run_allowed_command


def test_run_echo():
    allowed = AllowedCommand(exec="/bin/echo", fixed_args=[], working_dir=None, timeout=5)
    code, out, err = run_allowed_command(allowed, ["hello"], default_timeout=5)
    assert code == 0
    assert "hello" in out
    assert err == ""



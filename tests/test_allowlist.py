from mrlazy_bot.local_poller.allowlist import CommandAllowlist


def test_load_allowlist_example():
    allowlist = CommandAllowlist.load_from_yaml("config/commands.example.yaml")
    assert allowlist.get("echo") is not None



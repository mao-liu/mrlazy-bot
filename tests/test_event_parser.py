from mrlazy_bot.lambda_app.event_parser import extract_command_and_args, parse_message


def test_extract_command():
    cmd, args = extract_command_and_args("!mrlazy echo hello world")
    assert cmd == "echo"
    assert args == ["hello", "world"]


def test_parse_message_filters():
    assert parse_message({"event": {"type": "reaction_added"}}) is None
    assert parse_message({"event": {"type": "message", "subtype": "bot_message"}}) is None
    assert parse_message({"event": {"type": "message", "text": "hi"}}) is None



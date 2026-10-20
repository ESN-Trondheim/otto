from io import BytesIO
from unittest.mock import MagicMock, patch

from PIL import Image

import otto.slack  # noqa: F401 # Registers all commands on import
from otto.features.image_cache import retrieve_image
from otto.slack.app import _handle_command, handle_message
from otto.slack.command import commands
from tests.conftest import posted_texts


def test_all_commands_are_registered():
    assert {"help", "cover", "link", "qr"} <= commands.keys()


def test_help_lists_commands(event_args):
    args = event_args("help")

    _handle_command(args)

    (text,) = posted_texts(args)
    assert text.startswith("*Available commands*")
    assert "*help*: Get this list of all available commands." in text
    assert "*qr*: " in text


def test_command_is_matched_on_first_word(event_args):
    args = event_args("help me please")

    _handle_command(args)

    assert posted_texts(args)[0].startswith("*Available commands*")


def test_unknown_command(event_args):
    args = event_args("dance")

    _handle_command(args)

    assert "I don't recognize that command" in posted_texts(args)[0]


def test_unsupported_file_is_rejected(event_args):
    args = event_args(subtype="file_share", files=[{"filetype": "docx"}])

    with patch("otto.slack.app.requests.get") as get:
        handle_message(args)

    get.assert_not_called()
    assert "not a supported image" in args.say.call_args.args[0]
    assert retrieve_image(args.context.thread_ts) is None


def test_shared_image_is_stored_for_thread(event_args):
    args = event_args(
        subtype="file_share",
        files=[{"filetype": "png", "url_private": "https://files.slack.com/a.png"}],
    )
    args.client.token = "xoxb-test"
    png = BytesIO()
    Image.new("RGB", (20, 10)).save(png, format="PNG")

    with patch("otto.slack.app.requests.get") as get:
        get.return_value = MagicMock(content=png.getvalue())
        handle_message(args)

    get.assert_called_once_with(
        "https://files.slack.com/a.png",
        headers={"Authorization": "Bearer xoxb-test"},
    )
    assert retrieve_image(args.context.thread_ts).size == (20, 10)
    assert args.say.call_args.args[0].startswith("Nice image!")


def test_text_message_runs_command(event_args):
    args = event_args("dance")

    handle_message(args)

    assert "I don't recognize that command" in posted_texts(args)[0]

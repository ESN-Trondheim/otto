from io import BytesIO
from unittest.mock import MagicMock

import pytest
from PIL import Image
from slack_sdk.errors import SlackObjectFormationError

from otto.slack.utils.actions import transform_action_state_values
from otto.slack.utils.blocks import (
    actions,
    button,
    date_input,
    section,
    select_input,
    text_input,
)
from otto.slack.utils.messages import send_qr
from tests.conftest import date, plain, select, validate_messages


def test_transform_action_state_values():
    values = {
        "block-1": {"title": plain("Party"), "color": select("Cyan")},
        "block-2": {"date-from": date("2026-03-01"), "date-to": date(None)},
    }

    assert transform_action_state_values(values) == {
        "title": "Party",
        "color": "Cyan",
        "date-from": "2026-03-01",
        "date-to": None,
    }


def test_select_input_without_initial_option():
    block = select_input("Color", "color", ["Cyan", "Green"])

    assert [o["value"] for o in block["element"]["options"]] == ["Cyan", "Green"]
    assert "initial_option" not in block["element"]


def test_select_input_with_initial_option():
    block = select_input("Color", "color", ["Cyan", "Green"], initial_option="Green")

    assert block["element"]["initial_option"]["value"] == "Green"


def test_select_input_with_empty_initial_option_uses_first_option():
    block = select_input("Color", "color", ["Cyan", "Green"], initial_option="")

    assert block["element"]["initial_option"]["value"] == "Cyan"


def test_button_value_defaults_to_action_id():
    assert button("link.new", "New")["value"] == "link.new"
    assert button("link.qr", "QR", value="abc")["value"] == "abc"


def test_button_style_is_omitted_by_default():
    assert "style" not in button("link.new", "New")
    assert button("link.new", "New", style="danger")["style"] == "danger"


@pytest.mark.parametrize(
    "block",
    [
        section("hi"),
        text_input("Title", "title"),
        select_input("Color", "color", ["Cyan", "Green"], initial_option="Green"),
        date_input("Date", "date"),
        actions([button("a", "A"), button("b", "B", style="primary")]),
    ],
    ids=["section", "text", "select", "date", "actions"],
)
def test_blocks_are_valid(block):
    validate_messages(_message_with(block))


@pytest.mark.parametrize(
    "block",
    [
        actions([button("a", "A", style="default")]),
        section("x" * 3001),
        {**text_input("Title", "title"), "lable": "typo"},
    ],
    ids=["bad-style", "too-long", "unknown-key"],
)
def test_invalid_blocks_are_caught(block):
    with pytest.raises((SlackObjectFormationError, AssertionError)):
        validate_messages(_message_with(block))


def _message_with(block: dict):
    args = MagicMock()
    args.client.chat_postMessage(channel="C1", text="Fallback", blocks=[block])
    return args


def test_send_qr_uploads_jpeg_to_thread():
    args = MagicMock()
    args.body = {"container": {"channel_id": "C1", "thread_ts": "1.2"}}

    send_qr(args, "https://example.com")

    kwargs = args.client.files_upload_v2.call_args.kwargs
    assert kwargs["channel"] == "C1"
    assert kwargs["thread_ts"] == "1.2"
    assert kwargs["filename"] == "qr.jpg"
    assert Image.open(BytesIO(kwargs["content"])).format == "JPEG"

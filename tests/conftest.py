import os
from unittest.mock import MagicMock, patch

import pytest
from slack_sdk.models.blocks import Block

# Must be set before any otto module is imported, as the database connection and Slack app are created on import
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SLACK_BOT_TOKEN"] = "xoxb-test"
os.environ["SLACK_SIGNING_SECRET"] = "test-secret"

# The Slack app verifies its token against the Slack API when created, so this is stubbed for the whole test session
patch("slack_sdk.WebClient.auth_test", return_value=MagicMock()).start()

from otto.features import image_cache  # noqa: E402
from otto.persistence.redirect_link import RedirectLink  # noqa: E402

THREAD_TS = "1700000000.000100"


@pytest.fixture(autouse=True)
def clean_state():
    """Every test starts with an empty database and image cache"""
    RedirectLink.delete().execute()
    image_cache.images.clear()


def validate_messages(args):
    """Validates every message posted through the mocked client against Slack's Block Kit rules"""
    for call in args.client.chat_postMessage.call_args_list:
        message = call.kwargs

        assert message.get("text"), "Messages need fallback text for notifications"

        for block in message.get("blocks", []):
            parsed = Block.parse(block)
            parsed.validate_json()
            # Unknown or misspelled keys are dropped when parsing, so a lossless round trip proves there are none
            assert parsed.to_dict() == block


@pytest.fixture
def mocked_args():
    """Creates mocked Bolt args and validates the messages posted through them after the test"""
    created = []

    def create():
        args = MagicMock()
        created.append(args)
        return args

    yield create

    for args in created:
        validate_messages(args)


@pytest.fixture
def action_args(mocked_args):
    """Builds mocked Bolt args for a block action, with state values in the format Slack sends them"""

    def build(values: dict | None = None, action_value: str | None = None):
        args = mocked_args()
        args.body = {
            "container": {"channel_id": "C123", "thread_ts": THREAD_TS},
            "state": {"values": {"block": values or {}}},
            "actions": [{"value": action_value}],
        }
        return args

    return build


@pytest.fixture
def event_args(mocked_args):
    """Builds mocked Bolt args for a message event in an assistant thread"""

    def build(text: str = "", **event):
        args = mocked_args()
        args.event = {"channel": "C123", "thread_ts": THREAD_TS, "text": text, **event}
        args.context.channel_id = "C123"
        args.context.thread_ts = THREAD_TS
        return args

    return build


def plain(value: str | None):
    return {"type": "plain_text_input", "value": value}


def select(value: str):
    return {"type": "static_select", "selected_option": {"value": value}}


def date(value: str | None):
    return {"type": "datepicker", "selected_date": value}


def posted_texts(args) -> list[str]:
    return [c.kwargs.get("text") for c in args.client.chat_postMessage.call_args_list]

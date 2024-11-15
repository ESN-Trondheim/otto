import os

from slack_bolt import App, Assistant, Say
from slack_sdk import WebClient

from otto.command import extract_and_run_command

# Documentation: https://api.slack.com/docs/apps/ai
# Sample application: https://github.com/slack-samples/bolt-python-assistant-template/blob/main/listeners/events/assistant_thread_started.py

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN"),
)
assistant = Assistant()
app.use(assistant)


@assistant.thread_started
def assistant_thread_started(say: Say):
    """Handles the assistant_thread_started event: https://api.slack.com/events/assistant_thread_started"""
    say(text="Hey :wave: What would you like to do?")


@assistant.user_message
def message(event: dict, client: WebClient):
    """Handles the message event: https://api.slack.com/events/message.im"""
    extract_and_run_command(event, client)

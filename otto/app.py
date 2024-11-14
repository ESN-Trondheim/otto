import logging
import os

from slack_bolt import App, Assistant, Say, Ack
from slack_sdk import WebClient

from otto.commands import commands
from otto.blocks import section, actions, button

# Documentation: https://api.slack.com/docs/apps/ai
# Sample application: https://github.com/slack-samples/bolt-python-assistant-template/blob/main/listeners/events/assistant_thread_started.py

# Slack Bolt App is created and event handler functions are registered.
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)
assistant = Assistant()
app.use(assistant)


@assistant.thread_started
def assistant_thread_started(say: Say):
    """Handles the assistant_thread_started event: https://api.slack.com/events/assistant_thread_started"""
    logging.debug(f"New thread started")
    text = "Hey :wave: What would you like to do?"
    say(text=text, blocks=[
        section(text),
        actions([button(command.keyword, command.keyword) for command in commands.values()])
    ])


@assistant.user_message
def message(say: Say):
    """Handles the message event: https://api.slack.com/events/message.im"""
    say("Please use the buttons to select a command.")


@app.action()
def action(payload: dict, client: WebClient, ack: Ack):
    ack() # All Slack actions have to be acked.
    run_action_command(payload, client)

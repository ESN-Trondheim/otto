import logging
import os

from slack_bolt import App, Args, Assistant
from slack_bolt.adapter.socket_mode import SocketModeHandler
from waitress import serve

from otto.api import get_flask_api
from otto.slack.command import send_command_list

# Documentation: https://api.slack.com/docs/apps/ai
# Sample application: https://github.com/slack-samples/bolt-python-assistant-template/blob/main/listeners/events/assistant_thread_started.py

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN"),
)
assistant = Assistant()
app.use(assistant)


@assistant.thread_started
def handle_assistant_thread_started(args: Args):
    """Handles the assistant_thread_started event: https://api.slack.com/events/assistant_thread_started"""
    args.say(text="Hey :wave: Let me know what you would like to do!")
    send_command_list(args)


def start_slack_app():
    if os.environ.get("SOCKET_MODE") == "True":
        logging.info("Starting app in socket mode...")
        SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
    else:
        logging.info("Starting app in API mode...")
        serve(get_flask_api(app), host="0.0.0.0", port=os.environ.get("PORT", 8080))

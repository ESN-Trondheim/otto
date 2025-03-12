import logging
import os

from flask import Flask, redirect, request
from slack_bolt import App, Args, Assistant
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from waitress import serve

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

        slack_request_handler = SocketModeHandler(
            app, os.environ.get("SLACK_APP_TOKEN")
        )

        slack_request_handler.start()
    else:
        logging.info("Starting app in API mode...")

        slack_request_handler = SlackRequestHandler(app)
        api = Flask(__name__)

        @api.route("/qr/<link_id>")
        def _(qr_id: str):
            redirect(qr_id)

        @api.route("/slack/events", methods=["POST"])
        def _():
            """This is the main entry point of Slack events into the application"""
            return slack_request_handler.handle(request)

        serve(api, host="0.0.0.0", port=os.environ.get("PORT", 8080))

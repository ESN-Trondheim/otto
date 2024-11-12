import logging
import os

from dotenv import load_dotenv
from flask import Flask, request
from slack_bolt import App, Assistant, Say
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from waitress import serve

from blocks.welcome import welcome_message_blocks
from commands import extract_and_handle_command

logging.basicConfig(level=logging.INFO, force=True)
load_dotenv()

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
    say(blocks=welcome_message_blocks)


@assistant.user_message
def message(payload: dict, client: WebClient):
    """Handles the message event: https://api.slack.com/events/message.im"""
    logging.debug(f"Received message: '{payload["text"]}'")
    extract_and_handle_command(payload, client)


@app.middleware
def log_request(logger, body, next):
    """Logs all requests from Slack for debug purposes"""
    logger.debug(body)
    return next()


# When this file is executed directly the API is served either by opening a websocket connection to Slack for local development, or by exposing the Flask API.
if __name__ == "__main__":
    if os.environ.get("SOCKET_MODE") == "True":
        logging.info("Starting app in socket mode...")
        slack_request_handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
        slack_request_handler.start()
    else:
        logging.info("Starting app in API mode...")
        slack_request_handler = SlackRequestHandler(app)
        api = Flask(__name__)

        @api.route("/slack/events", methods=["POST"])
        def slack_events():
            """This is the main entry point of Slack events into the application"""
            return slack_request_handler.handle(request)
        
        serve(api, host="0.0.0.0", port=os.environ.get("PORT", 8080))

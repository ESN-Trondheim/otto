import os

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from waitress import serve

from commands import extract_and_handle_command

load_dotenv()

# Documentation: https://api.slack.com/docs/apps/ai
# Sample application: https://github.com/slack-samples/bolt-python-assistant-template/blob/main/listeners/events/assistant_thread_started.py

# Slack Bolt App is created and event handler functions are registered.
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


@app.event("assistant_thread_started")
def assistant_thread_started(event: dict, client: WebClient):
    """Handles the assistant_thread_started event: https://api.slack.com/events/assistant_thread_started"""
    thread = event["assistant_thread"]
    client.chat_postMessage(
        channel=thread["channel_id"],
        thread_ts=thread["thread_ts"],
        text=f"Hey there <@{thread["user_id"]}>! How can I help you today?",
    )


@app.event("message")
def message(event: dict, client: WebClient):
    """Handles the message event: https://api.slack.com/events/message.im"""
    extract_and_handle_command(event, client)


@app.middleware
def log_request(logger, body, next):
    """Logs all requests from Slack for debug purposes"""
    logger.debug(body)
    return next()


# Slack Bolt App is wrapped in a Flask adapter, and Flask API is used to handle incoming event requests.
api = Flask(__name__)
slack_handler = SlackRequestHandler(app)


@api.route("/slack/events", methods=["POST"])
def slack_events():
    """This is the main entry point of Slack events into the application"""
    return slack_handler.handle(request)


# When this file is executed directly the API is served.
if __name__ == "__main__":
    serve(api, host="0.0.0.0", port=os.environ.get("PORT", 8080))

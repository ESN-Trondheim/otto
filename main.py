import os
import logging

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request

from event_handlers import register_event_handlers

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# Documentation: https://api.slack.com/docs/apps/ai
# Sample application: https://github.com/slack-samples/bolt-python-assistant-template/blob/main/listeners/events/assistant_thread_started.py

# Slack Bolt App is created and event handler functions are registered.
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

register_event_handlers(app)

@app.middleware 
def log_request(logger, body, next):
    logger.debug(body)
    return next()

# Slack Bolt App is wrapped in a Flask adapter, and Flask API is used to handle incoming event requests.
api = Flask(__name__)
handler = SlackRequestHandler(app)

@api.route("/slack/events", methods=["POST"])
def slack_events():
    """This is the main entry point of Slack events into the application"""
    return handler.handle(request)

# When this file is executed directly the API is served.
if __name__ == "__main__":
    from waitress import serve
    serve(api, host="0.0.0.0", port=os.environ.get("PORT", 8080))
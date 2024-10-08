import os
import logging

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")

api = Flask(__name__)
handler = SlackRequestHandler(app)

@api.route("/slack/events", methods=["POST"])
def slack_events():
    """This is the main entry point of Slack events into the application"""
    return handler.handle(request)

if __name__ == "__main__":
    from waitress import serve
    serve(api, host="0.0.0.0", port=os.environ.get("PORT", 8080))
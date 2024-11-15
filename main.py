import logging
import os

from dotenv import load_dotenv
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from waitress import serve

logging.basicConfig(level=logging.INFO, force=True)
load_dotenv()

from otto.app import app

# When this file is executed directly the API is served either by opening a websocket connection to Slack for local development, or by exposing the Flask API.
if __name__ == "__main__":
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

        @api.route("/slack/events", methods=["POST"])
        def slack_events():
            """This is the main entry point of Slack events into the application"""
            return slack_request_handler.handle(request)

        serve(api, host="0.0.0.0", port=os.environ.get("PORT", 8080))

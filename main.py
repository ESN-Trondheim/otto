import logging
import sys

from dotenv import load_dotenv

from otto.slack.app import start_slack_app

sys.dont_write_bytecode = True
logging.basicConfig(level=logging.INFO, force=True)
load_dotenv()

# When this file is executed directly the API is served either by opening a websocket connection to Slack for local development, or by exposing the Flask API.
if __name__ == "__main__":
    start_slack_app()

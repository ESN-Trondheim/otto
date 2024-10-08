import os
import logging

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

dev_mode_enabled = bool(os.environ.get("DEV_MODE_ENABLED", False))
port = int(os.environ.get("PORT", 3000))

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")

if __name__ == "__main__":
    if dev_mode_enabled:
        SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
    else:
        app.start(port=port)
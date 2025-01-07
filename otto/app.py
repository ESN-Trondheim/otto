from os import environ
from io import BytesIO

import requests
from PIL import Image
from slack_bolt import App, Assistant, BoltContext, Say
from slack_sdk import WebClient

from otto.command import extract_and_run_command
from otto.image import store_image

# Documentation: https://api.slack.com/docs/apps/ai
# Sample application: https://github.com/slack-samples/bolt-python-assistant-template/blob/main/listeners/events/assistant_thread_started.py

app = App(
    signing_secret=environ.get("SLACK_SIGNING_SECRET"),
    token=environ.get("SLACK_BOT_TOKEN"),
)
assistant = Assistant()
app.use(assistant)


@assistant.thread_started
def handle_assistant_thread_started(say: Say):
    """Handles the assistant_thread_started event: https://api.slack.com/events/assistant_thread_started"""
    say(text="Hey :wave: What would you like to do?")


@assistant.user_message
def handle_message(context: BoltContext, event: dict, say: Say, client: WebClient):
    """Handles the message event: https://api.slack.com/events/message.im"""
    print(event)
    if hasattr(event, "files"):
        handle_file_share(context, event, say, client)
    else:
        extract_and_run_command(event, client)


def handle_file_share(context: BoltContext, event: dict, say: Say, client: WebClient):
    """Attempt to read received files as images"""

    # Get file info from Slack (https://api.slack.com/methods/files.info)
    file_info = client.files_info(file=event["file_id"]) 

    # Supported file extensions is extracted from Pillow
    supported_extensions = { e for e, f in Image.registered_extensions().items() if f in Image.OPEN }
    if not f".{file_info["filetype"]}" in supported_extensions:
        say("The file you sent is not a supported image type. Please try another format!")
        return

    # Read the response into a Pillow Image and store it for later.
    file_response = requests.get(file_info["file"]["url_private"], headers={"Authorization": f"Bearer {client.token}"})
    file_response.raise_for_status()
    store_image(context.thread_ts, Image.open(BytesIO(file_response.content)))

    say("Nice image! I will use it for the commands in this thread.")

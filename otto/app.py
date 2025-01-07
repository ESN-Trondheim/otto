import os
import requests

from slack_bolt import App, Assistant, Say
from slack_sdk import WebClient

from otto.command import extract_and_run_command
#from otto.image import

# Documentation: https://api.slack.com/docs/apps/ai
# Sample application: https://github.com/slack-samples/bolt-python-assistant-template/blob/main/listeners/events/assistant_thread_started.py

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN"),
)
app.use(Assistant())


@app.assistant.thread_started
def handle_assistant_thread_started(say: Say):
    """Handles the assistant_thread_started event: https://api.slack.com/events/assistant_thread_started"""
    say(text="Hey :wave: What would you like to do?")


@app.assistant.user_message
def handle_message(event: dict, client: WebClient):
    """Handles the message event: https://api.slack.com/events/message.im"""
    extract_and_run_command(event, client)


@app.event("file_shared")
def handle_file_shared(event, say, client: WebClient):
    file_id = event["file_id"]

    # API method docs: https://api.slack.com/methods/files.info
    file_info = client.files_info(file=file_id) 
    file_url = file_info["file"]["url_private"]
    
    response = requests.get(file_url, headers={"Authorization": f"Bearer {client.token}"})
    response.raise_for_status()

    # TODO: event["thread_id"]

    say("I've got the image!")

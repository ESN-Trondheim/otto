import os

from slack_bolt import App, Args, Assistant

from otto.command import handle_text_command, send_command_list
from otto.image import handle_image_share

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


@assistant.user_message
def handle_message(args: Args):
    """Handles the message event: https://api.slack.com/events/message.im"""
    if args.event.get("subtype", None) == "file_share":
        handle_image_share(args)
    else:
        handle_text_command(args)

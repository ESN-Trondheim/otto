import logging
from io import BytesIO

import requests
from PIL import Image
from slack_bolt import Args

from otto.features.image_cache import store_image
from otto.slack.app import assistant
from otto.slack.command import commands


@assistant.user_message
def handle_message(args: Args):
    """Handles the message event: https://api.slack.com/events/message.im"""
    if args.event.get("subtype", None) == "file_share":
        handle_image_share(args)
    else:
        handle_command(args)


def handle_command(args: Args):
    """Function to run a command based on a message event"""
    first_word = args.event["text"].split(" ")[0]
    logging.debug(f"Extracted command '{first_word}'")
    command = commands.get(first_word)

    if command:
        logging.debug(f"Running command function for '{command.keyword}'")
        command.function(args)
    else:
        logging.debug("Running unknown command function")
        args.client.chat_postMessage(
            channel=args.context.channel_id,
            thread_ts=args.context.thread_ts,
            text="I don't recognize that command. Please try again or type 'help' for a list of commands.",
        )


def handle_image_share(args: Args):
    """Attempt to read received files as images and store them for later"""

    file = args.event["files"][0]

    # Supported file extensions is extracted from Pillow
    supported_extensions = {
        e for e, f in Image.registered_extensions().items() if f in Image.OPEN
    }
    if f".{file["filetype"]}" not in supported_extensions:
        args.say(
            "The file you sent is not a supported image. Please try another format!"
        )
        return

    # Retrieve and store image
    file_response = requests.get(
        file["url_private"], headers={"Authorization": f"Bearer {args.client.token}"}
    )
    store_image(args.context.thread_ts, Image.open(BytesIO(file_response.content)))

    args.say(
        "Nice image! I will use it for everything image related from now on, until you make a new thread or replace it."
    )

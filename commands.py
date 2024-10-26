import io
import logging
from typing import Any, Callable

from slack_sdk import WebClient

from features.coverimage import create_cover_image


class Command:
    def __init__(
        self,
        function: Callable[[dict, WebClient], Any],
        keyword: str,
        description: str,
    ):
        self.function = function
        self.keyword = keyword
        self.description = description


# All registered commands will be kept in this dict
commands: dict[str, Command] = {}


def command(keyword: str, description: str) -> Callable:
    """Annotation used to annotate command handlers"""

    def register_command(function: Callable[[dict, WebClient], Any]):
        logging.debug(f"Registered command '{keyword}'")
        commands[keyword] = Command(function, keyword, description)

    return register_command


def extract_and_handle_command(event: dict, client: WebClient):
    first_word = event["text"].split(" ")[0]
    logging.debug(f"Extracted command '{first_word}'")
    command = commands.get(first_word)

    if command:
        logging.debug(f"Running command function for '{command.keyword}'")
        command.function(event, client)
    else:
        logging.debug(f"Running unknown command function")
        unknown_command(event, client)


def unknown_command(event: dict, client: WebClient):
    client.chat_postMessage(
        channel=event["channel"],
        thread_ts=event["thread_ts"],
        text="I don't recognize that command. Please try again or type 'help' for a list of commands.",
    )


@command("help", "Get this list of all available commands.")
def help(event: dict, client: WebClient):
    header = "*Available commands*\n\n"
    command_list = "\n".join([f"*{command.keyword}*: {command.description}" for command in commands.values()])

    client.chat_postMessage(
        channel=event["channel"],
        thread_ts=event["thread_ts"],
        text=header + command_list,
    )


@command(
    "coverimage",
    "Create a cover image based on the provided background picture and information.",
)
def coverimage(event: dict, client: WebClient):
    title = " ".join(event["text"].split(" ")[1:])
    coverimage = create_cover_image(title)
    image_content = io.BytesIO()

    coverimage.save(image_content, format="JPEG")
    client.files_upload_v2(content=image_content, channel=event["channel"], thread_ts=event["thread_ts"])

    client.chat_postMessage(
        channel=event["channel"],
        thread_ts=event["thread_ts"],
        text=f"<@{event["user"]}> said: '{event["text"]}'",
    )

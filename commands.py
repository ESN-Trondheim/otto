from typing import Callable

from slack_sdk import WebClient


class Command:
    def __init__(self, function: Callable[[dict, WebClient]], keyword: str, description: str):
        self.function = function
        self.keyword = keyword
        self.description = description


# All registered commands will be kept in this dict
commands: dict[str, Command] = {}


def command(keyword: str, description: str) -> Callable:
    """Annotation used to annotate command handlers"""

    def register_command(function: Callable[[dict, WebClient]]):
        commands[keyword] = Command(function, keyword, description)

    return register_command


def extract_and_handle_command(event: dict, client: WebClient):
    keyword = "coverimage" # TODO: Extract keyword from message
    commands.get(keyword).function(event, client)


@command("help", "Get this list of all available commands.")
def help(event: dict, client: WebClient):
    pass


@command("coverimage", "Create a cover image based on the provided background picture and information.")
def coverimage(event: dict, client: WebClient):
    client.chat_postMessage(
        channel=event["channel"],
        thread_ts=event["thread_ts"],
        text=f"<@{event["user"]}> said: '{event["text"]}'",
    )

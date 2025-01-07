import logging
from typing import Any, Callable

from slack_sdk import WebClient


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


def extract_and_run_command(event: dict, client: WebClient):
    """Function to run a command based on a message event"""
    first_word = event["text"].split(" ")[0]
    logging.debug(f"Extracted command '{first_word}'")
    command = commands.get(first_word)

    if command:
        logging.debug(f"Running command function for '{command.keyword}'")
        command.function(event, client)
    else:
        logging.debug(f"Running unknown command function")
        client.chat_postMessage(
            channel=event["channel"],
            thread_ts=event["thread_ts"],
            text="I don't recognize that command. Please try again or type 'help' for a list of commands.",
        )    


@command("help", "Get this list of all available commands.")
def help(event: dict, client: WebClient):
    header = "*Available commands*\n\n"
    command_list = "\n".join(
        [f"*{command.keyword}*: {command.description}" for command in commands.values()]
    )

    client.chat_postMessage(
        channel=event["channel"],
        thread_ts=event["thread_ts"],
        text=header + command_list,
    )

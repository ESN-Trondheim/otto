import logging
from typing import Any, Callable

from slack_bolt import Args


class Command:
    def __init__(
        self,
        function: Callable[[Args], Any],
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

    def register_command(function: Callable[[Args], Any]):
        logging.debug(f"Registered command '{keyword}'")
        commands[keyword] = Command(function, keyword, description)

        return function

    return register_command


@command("help", "Get this list of all available commands.")
def send_command_list(args: Args):
    header = "*Available commands*\n\n"
    command_list = "\n".join(
        [f"*{command.keyword}*: {command.description}" for command in commands.values()]
    )

    args.client.chat_postMessage(
        channel=args.context.channel_id,
        thread_ts=args.context.thread_ts,
        text=header + command_list,
    )


def handle_text_command(args: Args):
    """Function to run a command based on a message event"""
    first_word = args.event["text"].split(" ")[0]
    logging.debug(f"Extracted command '{first_word}'")
    command = commands.get(first_word)

    if command:
        logging.debug(f"Running command function for '{command.keyword}'")
        command.function(
            args
        )  # Using kwargs to pass all Slack functions to the handler.
    else:
        logging.debug("Running unknown command function")
        args.client.chat_postMessage(
            channel=args.context.channel_id,
            thread_ts=args.context.thread_ts,
            text="I don't recognize that command. Please try again or type 'help' for a list of commands.",
        )

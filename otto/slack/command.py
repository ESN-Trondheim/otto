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

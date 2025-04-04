import logging
from typing import Any, Callable

from slack_bolt import Args

from otto.features.cover import CoverFormat
from otto.features.image_cache import retrieve_image
from otto.slack.utils.blocks import (
    actions,
    button,
    date_input,
    select_input,
    text_input,
)
from otto.utils.esn import EsnColor


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


@command(
    "cover",
    "Create cover graphics for a digital platform.",
)
def cover(args: Args):
    args.client.chat_postMessage(
        channel=args.event["channel"],
        thread_ts=args.event["thread_ts"],
        text="Alright! Let's make some cover graphics :esnstar:",
    )

    if retrieve_image(args.event["thread_ts"]) is None:
        args.client.chat_postMessage(
            channel=args.event["channel"],
            thread_ts=args.event["thread_ts"],
            text=":warning: Remember to upload an image if you do not want me to use the default one. You can upload one right now and keep going if you'd like!",
        )

    args.client.chat_postMessage(
        channel=args.event["channel"],
        thread_ts=args.event["thread_ts"],
        text="Cover Generator",
        blocks=[
            text_input(text="Title (required)", value="title"),
            date_input(text="Date (from)", value="date-from"),
            date_input(text="Date (to)", value="date-to"),
            select_input(
                text="Color (required)",
                value="color",
                options=[c.display_name() for c in EsnColor],
            ),
            select_input(
                text="Format (required)",
                value="format",
                options=[f.value for f in CoverFormat],
            ),
            actions(
                elements=[
                    button(
                        action_id="cover.generate",
                        text="Generate",
                        style="primary",
                    )
                ]
            ),
        ],
    )


@command(
    "link",
    "Manage dynamic links and QR codes.",
)
def link(args: Args):
    args.client.chat_postMessage(
        channel=args.event["channel"],
        thread_ts=args.event["thread_ts"],
        text="Let's work those links :link: Are you looking to create a new link or change an existing link?",
    )

    args.client.chat_postMessage(
        channel=args.event["channel"],
        thread_ts=args.event["thread_ts"],
        text="Select Link",
        blocks=[
            actions(
                elements=[
                    button(action_id="link.new", text="Create a link", style="primary"),
                    button(
                        action_id="link.existing",
                        text="View or update a link",
                        style="primary",
                    ),
                ]
            ),
        ],
    )

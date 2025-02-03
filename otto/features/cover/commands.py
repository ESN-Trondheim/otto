from slack_bolt import Args

from otto.command import command
from otto.features.cover.generator import CoverFormat
from otto.image import retrieve_image
from otto.utils.blocks import (actions, button, date_input, select_input,
                               text_input)
from otto.utils.esn import EsnColor


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
                        text="Generate",
                        value="generate_cover_graphics",
                        style="primary",
                    )
                ]
            ),
        ],
    )

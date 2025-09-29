import io

from slack_bolt import Args

from otto.features.cover import CoverFormat, create_cover
from otto.features.image_cache import retrieve_image
from otto.slack.app import app
from otto.slack.command import command
from otto.slack.utils.actions import transform_action_state_values
from otto.slack.utils.blocks import (
    actions,
    button,
    date_input,
    select_input,
    text_input,
)
from otto.utils.date import format_date_range
from otto.utils.esn import EsnColor
from otto.utils.string import slugify_string


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


@app.action("cover.generate")
def generate_cover_graphics(args: Args):
    args.ack()

    # Apparently, args.context does not work for actions, so we have to use this instead.
    channel_id = args.body["container"]["channel_id"]
    thread_ts = args.body["container"]["thread_ts"]

    image = retrieve_image(thread_ts)
    state = transform_action_state_values(args.body["state"]["values"])

    # Either one date without
    subtitle = format_date_range(state["date-from"], state["date-to"])

    if image:
        cover = create_cover(
            title=state["title"],
            subtitle=subtitle,
            color=EsnColor.from_display_name(state["color"]),
            format=CoverFormat.from_value(state["format"]),
            background=image,
        )
    else:
        cover = create_cover(
            title=state["title"],
            subtitle=subtitle,
            color=EsnColor.from_display_name(state["color"]),
            format=CoverFormat.from_value(state["format"]),
        )

    image_content = io.BytesIO()
    cover.save(image_content, format="JPEG")

    args.client.chat_postMessage(
        channel=channel_id,
        thread_ts=thread_ts,
        text="Your cover image is on its way over!",
    )

    args.client.files_upload_v2(
        channel=channel_id,
        thread_ts=thread_ts,
        content=image_content.getvalue(),
        filename=f"{slugify_string(state["title"])}-cover.jpg",
    )

    args.client.chat_postMessage(
        channel=channel_id,
        thread_ts=thread_ts,
        text="Remember: You can change a couple of settings above and generate again if something is off.",
    )

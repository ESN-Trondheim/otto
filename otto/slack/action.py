import io

from slack_bolt import Args

from otto.features.cover import CoverFormat, create_cover
from otto.features.image_cache import retrieve_image
from otto.slack.app import app
from otto.slack.utils.actions import transform_action_state_values
from otto.utils.date import format_date_range
from otto.utils.esn import EsnColor
from otto.utils.string import slugify_string


@app.action("generate_cover_graphics")
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

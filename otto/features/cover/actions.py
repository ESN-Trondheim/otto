import io
from datetime import date

from slack_bolt import Args

from otto.app import app
from otto.features.cover.generator import CoverFormat, create_cover
from otto.image import retrieve_image
from otto.utils.actions import transform_action_state_values
from otto.utils.esn import EsnColor


@app.action("generate_cover_graphics")
def generate_cover_graphics(args: Args):
    args.ack()

    # Apparently, args.context does not work for actions, so we have to use this instead.
    channel_id = args.body["container"]["channel_id"]
    thread_ts = args.body["container"]["thread_ts"]

    image = retrieve_image(thread_ts)
    state = transform_action_state_values(args.body["state"]["values"])

    subtitle = date.fromisoformat(state["date"]).strftime("%x")

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
        filename="cover.png",
    )

    args.client.chat_postMessage(
        channel=channel_id,
        thread_ts=thread_ts,
        text="Remember: You can change a couple of settings above and generate again if something is off.",
    )

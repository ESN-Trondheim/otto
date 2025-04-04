import io

import qrcode
from slack_bolt import Args

from otto.features.cover import CoverFormat, create_cover
from otto.features.image_cache import retrieve_image
from otto.persistence.redirect_link import RedirectLink
from otto.slack.app import app
from otto.slack.utils.actions import transform_action_state_values
from otto.slack.utils.blocks import actions, button, select_input, text_input
from otto.slack.utils.messages import send_qr
from otto.utils.date import format_date_range
from otto.utils.esn import EsnColor
from otto.utils.string import slugify_string


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


@app.action("link.new")
@app.action("link.selected")
def link_new(args: Args):
    args.ack()
    state = transform_action_state_values(args.body["state"]["values"])
    link_id = state.get("link.selected", None)

    if link_id is None:
        args.client.chat_postMessage(
            channel=args.body["container"]["channel_id"],
            thread_ts=args.body["container"]["thread_ts"],
            text="Create Link",
            blocks=[
                text_input("Link ID (required)", "id"),
                text_input("URL (required)", "url"),
                actions(
                    elements=[
                        button(
                            action_id="link.submit",
                            text="Create new link",
                            style="primary"
                        ),
                    ]
                ),
            ]
        )
    else:
        url = RedirectLink.get_link_url_by_id(link_id)
        args.client.chat_postMessage(
            channel=args.body["container"]["channel_id"],
            thread_ts=args.body["container"]["thread_ts"],
            text=f"The link '{link_id}' currently points to '{url}'. You can change the destination and get a QR code below.",
        )

        args.client.chat_postMessage(
            channel=args.body["container"]["channel_id"],
            thread_ts=args.body["container"]["thread_ts"],
            text="Create Link",
            blocks=[
                text_input("URL (required)", "url"),
                actions(
                    elements=[
                        button(
                            action_id="link.submit",
                            text="Update link",
                            value=link_id,
                            style="primary"
                        ),
                        button(
                            action_id="link.qr",
                            text="Get QR code for link",
                            value=link_id,
                            style="primary"
                        ),
                        button(
                            action_id="link.delete",
                            text="Delete link",
                            value=link_id,
                            style="danger"
                        ),
                    ]
                ),
            ]
        )


@app.action("link.existing")
def link_existing(args: Args):
    args.ack()
    args.client.chat_postMessage(
        channel=args.body["container"]["channel_id"],
        thread_ts=args.body["container"]["thread_ts"],
        text="Select Link",
        blocks=[
            select_input(
                text="Link",
                value="link.selected",
                options=[link.id for link in RedirectLink.select()]
            )
        ]
    )


@app.action("link.submit")
@app.action("link.qr")
def link_update(args: Args):
    args.ack()

    state = transform_action_state_values(args.body["state"]["values"])
    existing_link = state.get("id", None) is None
    link_id = state.get("id", args.body["actions"][0]["value"])
    url = state["url"]

    if url and existing_link:
        link = RedirectLink.get(id=link_id)
        link.url = url
        link.save()
    elif url:
        RedirectLink.create(id=link_id, url=url)
    
    if url:
        args.client.chat_postMessage(
            channel=args.body["container"]["channel_id"],
            thread_ts=args.body["container"]["thread_ts"],
            text=f"The link '{link_id}' ready to go!",
        )

    send_qr(args, link_id)


@app.action("link.delete")
def link_delete(args: Args):
    args.ack()
    link_id = args.body["actions"][0]["value"]
    RedirectLink.delete().where(RedirectLink.id == link_id).execute()
    args.client.chat_postMessage(
        channel=args.body["container"]["channel_id"],
        thread_ts=args.body["container"]["thread_ts"],
        text=f"The link '{link_id}' was deleted :wastebasket:",
    )
from slack_bolt import Args

from otto.persistence.redirect_link import RedirectLink
from otto.slack.app import app
from otto.slack.command import command
from otto.slack.utils.actions import transform_action_state_values
from otto.slack.utils.blocks import actions, button, select_input, text_input
from otto.slack.utils.messages import send_qr


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
                            style="primary",
                        ),
                    ]
                ),
            ],
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
                            style="primary",
                        ),
                        button(
                            action_id="link.qr",
                            text="Get QR code for link",
                            value=link_id,
                            style="primary",
                        ),
                        button(
                            action_id="link.delete",
                            text="Delete link",
                            value=link_id,
                            style="danger",
                        ),
                    ]
                ),
            ],
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
                options=[link.id for link in RedirectLink.select()],
            )
        ],
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

    send_qr(args, f"https://links.trondheim.esn.no/link/{link_id}")


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

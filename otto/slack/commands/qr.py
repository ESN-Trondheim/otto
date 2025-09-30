from slack_bolt import Args

from otto.slack.app import app
from otto.slack.command import command
from otto.slack.utils.actions import transform_action_state_values
from otto.slack.utils.blocks import actions, button, text_input
from otto.slack.utils.messages import send_qr


@command(
    "qr",
    "Create a QR code from a static URL.",
)
def qr(args: Args):
    args.client.chat_postMessage(
        channel=args.event["channel"],
        thread_ts=args.event["thread_ts"],
        text="Let's create a QR code :technologist: Type the content of the code in the field below!",
    )

    args.client.chat_postMessage(
        channel=args.event["channel"],
        thread_ts=args.event["thread_ts"],
        text="Create QR code",
        blocks=[
            text_input("URL (required)", "url"),
            actions(
                elements=[
                    button(
                        action_id="qr.create",
                        text="Create QR code",
                        style="primary",
                    ),
                ]
            ),
        ],
    )


@app.action("qr.create")
def qr_create(args: Args):
    args.ack()

    state = transform_action_state_values(args.body["state"]["values"])
    url = state["url"]

    if url:
        args.client.chat_postMessage(
            channel=args.body["container"]["channel_id"],
            thread_ts=args.body["container"]["thread_ts"],
            text=f"The QR code for '{url}' is ready!",
        )
        send_qr(args, url)
    else:
        args.client.chat_postMessage(
            channel=args.body["container"]["channel_id"],
            thread_ts=args.body["container"]["thread_ts"],
            text="You need to provide a URL for me to create a QR code...",
        )

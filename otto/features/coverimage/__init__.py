from slack_bolt import BoltContext
from slack_sdk import WebClient

from otto.command import command
from otto.image import retrieve_image
from otto.features.coverimage.ui import COVERIMAGE_BLOCKS


@command(
    "coverimage",
    "Create a cover image based on the provided background picture and information.",
)
def coverimage(event: dict, context: BoltContext, client: WebClient):
    client.chat_postMessage(
        channel=event["channel"],
        thread_ts=event["thread_ts"],
        text="This command relies on Slack blocks to work properly.",
        blocks=COVERIMAGE_BLOCKS,
    )

    if retrieve_image(context.thread_ts) is None:
        client.chat_postMessage(
            channel=context.channel_id,
            thread_ts=context.thread_ts,
            text=":warning: I will use the default picture if you don't upload one :warning:"
        )
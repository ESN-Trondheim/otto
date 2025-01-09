from slack_bolt import Args

from otto.command import command
from otto.image import retrieve_image
from otto.features.coverimage.blocks import COVERIMAGE_BLOCKS


@command(
    "coverimage",
    "Create a cover image based on the provided background picture and information.",
)
def coverimage(args: Args):
    args.client.chat_postMessage(
        channel=args.event["channel"],
        thread_ts=args.event["thread_ts"],
        text="Alright! Let's make a cover image :esnstar:",
        blocks=COVERIMAGE_BLOCKS,
    )

    if retrieve_image(args.event["thread_ts"]) is None:
        args.client.chat_postMessage(
            channel=args.event["channel"],
            thread_ts=args.event["thread_ts"],
            text=":warning: I will use the default picture if you don't upload one now :warning:"
        )
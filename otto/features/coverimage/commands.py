from slack_bolt import Args

from otto.command import command
from otto.features.coverimage.blocks import COVERIMAGE_BLOCKS
from otto.image import retrieve_image


@command(
    "coverimage",
    "Create a cover image based on the provided background picture and information.",
)
def coverimage(args: Args):
    args.client.chat_postMessage(
        channel=args.event["channel"],
        thread_ts=args.event["thread_ts"],
        text="Alright! Let's make a cover image :esnstar:",
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
        text="Coverimage Generator",
        blocks=COVERIMAGE_BLOCKS,
    )

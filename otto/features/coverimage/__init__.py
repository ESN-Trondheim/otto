import io

from slack_bolt import BoltContext
from slack_sdk import WebClient

from otto.command import command
from otto.image import retrieve_image
from otto.features.coverimage.generator import create_cover_image


@command(
    "coverimage",
    "Create a cover image based on the provided background picture and information.",
)
def coverimage(event: dict, context: BoltContext, client: WebClient):

    title = " ".join(event["text"].split(" ")[1:])

    image = retrieve_image(context.thread_ts)
    if image:
        coverimage = create_cover_image(title, background=image)
    else:
        coverimage = create_cover_image(title)

    image_content = io.BytesIO()
    coverimage.save(image_content, format="JPEG")
    client.files_upload_v2(
        content=image_content.getvalue(),
        channel=event["channel"],
        thread_ts=event["thread_ts"],
    )
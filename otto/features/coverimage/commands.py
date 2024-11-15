import io

from slack_sdk import WebClient

from otto.command import command
from otto.features.coverimage.generator import create_cover_image


@command(
    "coverimage",
    "Create a cover image based on the provided background picture and information.",
)
def coverimage(event: dict, client: WebClient):
    title = " ".join(event["text"].split(" ")[1:])
    coverimage = create_cover_image(title)
    image_content = io.BytesIO()

    coverimage.save(image_content, format="JPEG")
    client.files_upload_v2(
        content=image_content.getvalue(),
        channel=event["channel"],
        thread_ts=event["thread_ts"],
    )

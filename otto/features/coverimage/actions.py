from slack_bolt import Ack
from slack_sdk import WebClient
from otto import app


@app.action()
def generate_coverimage(ack: Ack, client: WebClient, body: dict):
    title = " ".join(event["text"].split(" ")[1:])
    coverimage = create_cover_image(title)
    image_content = io.BytesIO()

    coverimage.save(image_content, format="JPEG")
    client.files_upload_v2(
        content=image_content.getvalue(),
        channel=event["channel"],
        thread_ts=event["thread_ts"],
    )
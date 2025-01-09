import io

from slack_bolt import Ack
from slack_sdk import WebClient

from otto import app
from otto.features.coverimage.generator import create_cover_image
from otto.image import retrieve_image
from otto.utils.actions import transform_action_state_values
from otto.utils.blocks import actions, button, section, select_input, text_input
from otto.utils.esn import EsnColor


COVERIMAGE_BLOCKS = [
    section(text="Alright! Let's make a cover image :esnstar:"),
    text_input(text="Title", value="title"),
    text_input(text="Subtitle", value="subtitle"),
    text_input(text="Subsubtitle", value="subsubtitle"),
    select_input(text="Color", value="color", options=[c.name for c in EsnColor]),
    actions(elements=[button(text="Generate", value="generate_coverimage")])
]


@app.action("generate_coverimage")
def coverimage(body: dict, client: WebClient, ack: Ack):
    ack()

    thread_ts = body["container"]["thread_ts"]
    channel_id = body["container"]["channel_id"]
    state = transform_action_state_values(body["state"]["values"])
    image = retrieve_image(thread_ts)

    if image:
        coverimage = create_cover_image(title=state['title'], subtitle=state['subtitle'], subsubtitle=state['subsubtitle'], color=EsnColor[state['color']], background=image)
    else:
        coverimage = create_cover_image(title=state['title'], subtitle=state['subtitle'], subsubtitle=state['subsubtitle'], color=EsnColor[state['color']])

    image_content = io.BytesIO()
    coverimage.save(image_content, format="JPEG")

    client.files_upload_v2(
        content=image_content.getvalue(),
        thread_ts=thread_ts,
        channel=channel_id
    )
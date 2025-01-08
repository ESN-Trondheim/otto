import io

from slack_bolt import Ack, BoltContext
from slack_sdk import WebClient

from otto import app
from otto.features.coverimage.generator import create_cover_image
from otto.image import retrieve_image
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
def coverimage(action: dict, context: BoltContext, client: WebClient, ack: Ack):
    ack()

    print(action)
    
    image = retrieve_image(context.thread_ts)
    if image:
        coverimage = create_cover_image(title=action['title'], subtitle=action['subtitle'], subsubtitle=action['subsubtitle'], color=EsnColor[action['color']], background=image)
    else:
        coverimage = create_cover_image(title=action['title'], subtitle=action['subtitle'], subsubtitle=action['subsubtitle'], color=EsnColor[action['color']])

    image_content = io.BytesIO()
    coverimage.save(image_content, format="JPEG")

    client.files_upload_v2(
        content=image_content.getvalue(),
        channel=context.channel_id,
        thread_ts=context.thread_ts,
    )
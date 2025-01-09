from datetime import datetime, timedelta
from io import BytesIO

from PIL.Image import Image
import requests
from slack_bolt import Args


class TimestampedImage:
    def __init__(
        self,
        image: Image,
    ):
        self.image = image
        self.time = datetime.now()


# All images are kept in memory using this dictionary.
images: dict[str, TimestampedImage] = {}


def store_image(id: str, image: Image):
    remove_old_images()
    images[id] = TimestampedImage(image)


def retrieve_image(id: str) -> Image | None:
    remove_old_images()
    ts_image = images.get(id, None)

    if ts_image is None:
        return None
    
    return ts_image.image


def remove_old_images():
    now = datetime.now()
    for id, timestamped_image in images.items():
        age = now - timestamped_image.time

        if age > timedelta(hours=24):
            images.remove(id)


def handle_image_share(args: Args):
    """Attempt to read received files as images and store them for later"""

    file = args.event["files"][0]

    # Supported file extensions is extracted from Pillow
    supported_extensions = { e for e, f in Image.registered_extensions().items() if f in Image.OPEN }
    if not f".{file["filetype"]}" in supported_extensions:
        args.say("The file you sent is not a supported image. Please try another format!")
        return

    # Retrieve and store image
    file_response = requests.get(file["url_private"], headers={"Authorization": f"Bearer {args.client.token}"})
    store_image(args.event["thread_ts"], Image.open(BytesIO(file_response.content)))

    args.say("Nice image! I will use it for the commands in this thread.")
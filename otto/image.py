from datetime import datetime, timedelta

from PIL.Image import Image


class TimestampedImage:
    def __init__(
        self,
        image: Image,
        time: datetime,
    ):
        self.image = image
        self.time = time


images: dict[str, TimestampedImage] = {}


def add_image(id: str, image: Image):
    remove_old_images()
    images[id] = TimestampedImage(image, datetime.now())


def get_image(thread_id: str) -> Image | None:
    remove_old_images()
    return images.get(thread_id, None)


def remove_old_images():
    now = datetime.now()
    for thread_id, ts_image in images.items():
        age = now - ts_image.time
        if age > timedelta(hours=24):
            images.remove(thread_id)
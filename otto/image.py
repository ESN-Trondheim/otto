from datetime import datetime, timedelta

from PIL.Image import Image


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
    return images.get(id, None).image


def remove_old_images():
    now = datetime.now()
    for id, timestamped_image in images.items():
        age = now - timestamped_image.time

        if age > timedelta(hours=24):
            images.remove(id)
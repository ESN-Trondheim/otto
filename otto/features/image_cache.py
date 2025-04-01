from datetime import datetime, timedelta

from PIL.Image import Image as ImageClass

images: dict[str, (ImageClass, datetime)] = {}


def store_image(id: str, image: ImageClass):
    remove_old_images()
    images[id] = (image, datetime.now())


def retrieve_image(id: str) -> ImageClass | None:
    remove_old_images()

    result = images.get(id, None)

    if result is None:
        return None

    # Unpack result of type (ImageClass, datetime)
    image, _ = result

    return image


def remove_old_images():
    now = datetime.now()

    for id, (_, time) in list(images.items()):
        age = now - time

        if age > timedelta(hours=24):
            images.pop(id)

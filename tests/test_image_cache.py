from datetime import datetime, timedelta

from PIL import Image

from otto.features import image_cache
from otto.features.image_cache import retrieve_image, store_image


def test_store_and_retrieve_image():
    image = Image.new("RGB", (10, 10))
    store_image("thread", image)

    assert retrieve_image("thread") is image


def test_retrieve_missing_image():
    assert retrieve_image("missing") is None


def test_images_older_than_a_day_are_removed():
    image = Image.new("RGB", (10, 10))
    image_cache.images["old"] = (image, datetime.now() - timedelta(hours=25))
    image_cache.images["recent"] = (image, datetime.now() - timedelta(hours=23))

    assert retrieve_image("old") is None
    assert retrieve_image("recent") is image

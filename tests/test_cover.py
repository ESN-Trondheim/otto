import pytest
from PIL import Image

from otto.features.cover import (
    CoverFormat,
    add_color_layer,
    create_cover,
    resize_and_crop_to_dimension,
)
from otto.utils.esn import EsnColor


@pytest.mark.parametrize("cover_format", list(CoverFormat))
def test_create_cover_matches_format_size(cover_format):
    cover = create_cover("Title", subtitle="Subtitle", format=cover_format)

    assert cover.size == cover_format.size
    assert cover.mode == "RGB"


def test_create_cover_with_custom_background():
    background = Image.new("RGBA", (500, 2000), (255, 0, 0, 255))
    cover = create_cover("Title", background=background)

    assert cover.size == CoverFormat.ESN_ACTIVITIES.size


@pytest.mark.parametrize(
    "size",
    [(100, 1000), (5000, 100), (1920, 460), (3840, 920), (10, 10), (1921, 461)],
    ids=["tall", "wide", "exact", "same-ratio", "tiny", "odd-crop"],
)
def test_resize_and_crop_to_dimension(size):
    image = Image.new("RGB", size)

    assert resize_and_crop_to_dimension(image, 1920, 460).size == (1920, 460)


def test_add_color_layer_tints_image():
    image = Image.new("RGB", (4, 4), (0, 0, 0))
    tinted = add_color_layer(image, EsnColor.CYAN)

    assert tinted.getpixel((0, 0)) == tuple(round(c * 0.6) for c in (0, 174, 239))


def test_cover_format_from_value():
    assert CoverFormat.from_value("Hoopla") is CoverFormat.HOOPLA
    assert CoverFormat.from_value("Instagram") is None

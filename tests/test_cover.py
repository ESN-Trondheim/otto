import pytest
from PIL import Image

from otto.features.cover import (
    CoverFormat,
    assets,
    create_cover,
    layout_lines,
    render_cover_html,
    resize_and_crop_to_dimension,
)
from otto.utils.esn import EsnColor


@pytest.mark.parametrize("cover_format", list(CoverFormat))
def test_every_format_has_a_template_of_the_same_size(cover_format):
    template = assets.joinpath("templates", cover_format.template).read_text()

    assert f"width: {cover_format.target_width}px;" in template
    assert f"height: {cover_format.target_height}px;" in template


@pytest.mark.parametrize("cover_format", list(CoverFormat))
def test_create_cover_matches_format_size(cover_format):
    cover = create_cover("Title", subtitle="Subtitle", format=cover_format)

    assert cover.size == cover_format.size
    assert cover.mode == "RGB"


def test_create_cover_with_custom_background():
    background = Image.new("RGBA", (500, 2000), (255, 0, 0, 255))
    cover = create_cover("Title", background=background)

    assert cover.size == CoverFormat.ESN_ACTIVITIES.size
    # The bottom left corner is the red background, blended 60% with the default dark blue
    pixel = cover.getpixel((5, cover.height - 5))
    assert all(abs(p - e) <= 3 for p, e in zip(pixel, (130, 29, 88)))


def test_render_cover_html_fills_template():
    html = render_cover_html("Title", subtitle="Subtitle", color=EsnColor.CYAN)

    assert ">Title</p>" in html
    assert ">Subtitle</p>" in html
    assert "background-color: rgba(0, 174, 239, 0.6)" in html
    assert "data:image/png;base64," in html


def test_render_cover_html_escapes_text():
    html = render_cover_html("<script>alert(1)</script>")

    assert "<script>" not in html
    assert "&lt;script&gt;" in html


@pytest.mark.parametrize(
    ("subtitle", "sizes"), [(None, [90]), ("Subtitle", [90, 50])], ids=["solo", "both"]
)
def test_layout_lines_uses_cover_fonts(subtitle, sizes):
    lines = layout_lines(CoverFormat.HOOPLA, "Title", subtitle)

    assert [line["size"] for line in lines] == sizes


def test_layout_lines_moves_title_up_for_subtitle():
    (solo,) = layout_lines(CoverFormat.ESN_ACTIVITIES, "Title", None)
    title, subtitle = layout_lines(CoverFormat.ESN_ACTIVITIES, "Title", "Subtitle")

    assert title["y"] < solo["y"] < subtitle["y"]
    assert title["x"] == solo["x"]


@pytest.mark.parametrize(
    "size",
    [(100, 1000), (5000, 100), (1920, 460), (3840, 920), (10, 10), (1921, 461)],
    ids=["tall", "wide", "exact", "same-ratio", "tiny", "odd-crop"],
)
def test_resize_and_crop_to_dimension(size):
    image = Image.new("RGB", size)

    assert resize_and_crop_to_dimension(image, 1920, 460).size == (1920, 460)


def test_cover_format_from_value():
    assert CoverFormat.from_value("Hoopla") is CoverFormat.HOOPLA
    assert CoverFormat.from_value("Instagram") is None

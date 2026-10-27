from io import BytesIO
from unittest.mock import patch

import pytest
from PIL import Image

from otto.features import cover as cover_feature
from otto.features.image_cache import store_image
from otto.persistence.redirect_link import RedirectLink
from otto.slack.commands.cover import cover, generate_cover_graphics
from otto.slack.commands.link import (
    link,
    link_delete,
    link_existing,
    link_new,
    link_update,
)
from otto.slack.commands.qr import qr, qr_create
from tests.conftest import THREAD_TS, date, plain, posted_texts, select


def cover_values(**overrides):
    values = {
        "format": select("Facebook"),
        "color": select("Cyan"),
        "title": plain("Summer Party!"),
        "date-from": date("2026-06-01"),
        "date-to": date("2026-06-03"),
        "custom-subtitle": plain(None),
    }
    return values | overrides


def test_cover_warns_when_no_image_is_uploaded(event_args):
    args = event_args("cover")

    cover(args)

    assert any("Remember to upload an image" in t for t in posted_texts(args))


def test_cover_does_not_warn_when_image_is_uploaded(event_args):
    store_image(THREAD_TS, Image.new("RGB", (10, 10)))
    args = event_args("cover")

    cover(args)

    assert not any("Remember to upload an image" in t for t in posted_texts(args))


@pytest.mark.parametrize(
    ("custom_subtitle", "expected_subtitle"),
    [(None, "1st - 3rd of June"), ("Sold out", "Sold out")],
)
def test_generate_cover_graphics(action_args, custom_subtitle, expected_subtitle):
    args = action_args(cover_values(**{"custom-subtitle": plain(custom_subtitle)}))

    with patch(
        "otto.slack.commands.cover.create_cover", wraps=cover_feature.create_cover
    ) as create_cover:
        generate_cover_graphics(args)

    args.ack.assert_called_once()
    assert create_cover.call_args.kwargs["subtitle"] == expected_subtitle
    upload = args.client.files_upload_v2.call_args.kwargs
    assert upload["filename"] == "summer-party-cover.jpg"
    image = Image.open(BytesIO(upload["content"]))
    assert (image.format, image.size) == ("JPEG", (1568, 588))


def test_generate_cover_graphics_uses_uploaded_image(action_args):
    background = Image.new("RGB", (100, 100))
    store_image(THREAD_TS, background)
    args = action_args(cover_values())

    with patch("otto.slack.commands.cover.create_cover") as create_cover:
        create_cover.return_value = Image.new("RGB", (10, 10))
        generate_cover_graphics(args)

    assert create_cover.call_args.kwargs["background"] is background


def test_link_offers_new_or_existing(event_args):
    args = event_args("link")

    link(args)

    blocks = args.client.chat_postMessage.call_args.kwargs["blocks"]
    action_ids = [e["action_id"] for e in blocks[0]["elements"]]
    assert action_ids == ["link.new", "link.existing"]


def test_link_new_shows_create_form(action_args):
    args = action_args()

    link_new(args)

    blocks = args.client.chat_postMessage.call_args.kwargs["blocks"]
    assert [b["element"]["action_id"] for b in blocks[:2]] == ["id", "url"]


def test_link_selected_shows_current_url(action_args):
    RedirectLink.create(id="party", url="https://example.com")
    args = action_args({"link.selected": select("party")})

    link_new(args)

    assert "'party' currently points to 'https://example.com'" in posted_texts(args)[0]


def test_link_existing_lists_links(action_args):
    RedirectLink.create(id="a", url="https://a.com")
    RedirectLink.create(id="b", url="https://b.com")
    args = action_args()

    link_existing(args)

    block = args.client.chat_postMessage.call_args.kwargs["blocks"][0]
    assert [o["value"] for o in block["element"]["options"]] == ["a", "b"]


def test_link_existing_without_links(action_args):
    args = action_args()

    link_existing(args)

    assert posted_texts(args) == ["There are no links yet. Create one to get started!"]


def test_link_submit_creates_new_link(action_args):
    args = action_args({"id": plain("party"), "url": plain("https://example.com")})

    with patch("otto.slack.commands.link.send_qr") as send_qr:
        link_update(args)

    assert RedirectLink.get_link_url_by_id("party") == "https://example.com"
    send_qr.assert_called_once_with(args, "https://links.trondheim.esn.no/link/party")


def test_link_submit_updates_existing_link(action_args):
    RedirectLink.create(id="party", url="https://old.com")
    args = action_args({"url": plain("https://new.com")}, action_value="party")

    with patch("otto.slack.commands.link.send_qr"):
        link_update(args)

    assert RedirectLink.get_link_url_by_id("party") == "https://new.com"
    assert RedirectLink.select().count() == 1


def test_link_qr_without_url_only_sends_qr(action_args):
    RedirectLink.create(id="party", url="https://example.com")
    args = action_args({"url": plain(None)}, action_value="party")

    with patch("otto.slack.commands.link.send_qr") as send_qr:
        link_update(args)

    assert RedirectLink.get_link_url_by_id("party") == "https://example.com"
    args.client.chat_postMessage.assert_not_called()
    send_qr.assert_called_once()


def test_link_delete(action_args):
    RedirectLink.create(id="party", url="https://example.com")
    RedirectLink.create(id="other", url="https://example.com")
    args = action_args(action_value="party")

    link_delete(args)

    assert [l.id for l in RedirectLink.select()] == ["other"]
    assert "'party' was deleted" in posted_texts(args)[0]


def test_qr_shows_form(event_args):
    args = event_args("qr")

    qr(args)

    blocks = args.client.chat_postMessage.call_args.kwargs["blocks"]
    assert blocks[1]["elements"][0]["action_id"] == "qr.create"


def test_qr_create(action_args):
    args = action_args({"url": plain("https://example.com")})

    with patch("otto.slack.commands.qr.send_qr") as send_qr:
        qr_create(args)

    send_qr.assert_called_once_with(args, "https://example.com")


def test_qr_create_without_url(action_args):
    args = action_args({"url": plain(None)})

    with patch("otto.slack.commands.qr.send_qr") as send_qr:
        qr_create(args)

    send_qr.assert_not_called()
    assert "You need to provide a URL" in posted_texts(args)[0]

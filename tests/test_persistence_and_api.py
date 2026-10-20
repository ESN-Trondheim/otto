from unittest.mock import MagicMock

import pytest
from peewee import DoesNotExist

from otto.api import get_flask_api
from otto.persistence.redirect_link import RedirectLink


def test_get_link_url_by_id():
    RedirectLink.create(id="party", url="https://example.com/party")

    assert RedirectLink.get_link_url_by_id("party") == "https://example.com/party"


def test_get_link_url_by_unknown_id_raises():
    with pytest.raises(DoesNotExist):
        RedirectLink.get_link_url_by_id("missing")


@pytest.fixture
def client():
    return get_flask_api(MagicMock()).test_client()


def test_link_redirects_to_stored_url(client):
    RedirectLink.create(id="party", url="https://example.com/party")

    response = client.get("/link/party")

    assert response.status_code == 302
    assert response.location == "https://example.com/party"


def test_unknown_link_redirects_to_fallback(client):
    response = client.get("/link/missing")

    assert response.status_code == 302
    assert response.location == "https://trondheim.esn.no"

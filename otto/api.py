from flask import Flask, redirect, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from otto.persistence.redirect_link import RedirectLink


def get_flask_api(app: App):
    slack_request_handler = SlackRequestHandler(app)
    api = Flask(__name__)

    @api.route("/link/<link_id>")
    def _(link_id: str):
        redirect(RedirectLink.get(id=link_id))

    @api.route("/slack/events", methods=["POST"])
    def _():
        """This is the main entry point of Slack events into the application"""
        return slack_request_handler.handle(request)

    return api

from flask import Flask, redirect, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from otto.persistence.redirect_link import RedirectLink


def get_flask_api(app: App):
    slack_request_handler = SlackRequestHandler(app)
    api = Flask(__name__)

    @api.route("/slack/events", methods=["POST"])
    def handle_slack():
        """This is the main entry point of Slack events into the application"""
        return slack_request_handler.handle(request)

    @api.route("/link/<link_id>")
    def handle_link(link_id: str):
        """This is the entry point for short links into the application"""
        return redirect(RedirectLink.get_link_url_by_id(link_id))

    return api

from slack_bolt import App
from slack_sdk import WebClient

# This file contains event handlers for the Slack Bolt app

def register_event_handlers(app: App):
    @app.event("assistant_thread_started")
    def assistant_thread_started(event, client: WebClient):
        """Handles the assistant_thread_started event: https://api.slack.com/events/assistant_thread_started"""
        thread = event["assistant_thread"]
        client.chat_postMessage(
            channel=thread["channel_id"], 
            thread_ts=thread["thread_ts"],
            text=f"Hey there <@{thread["user_id"]}>! How can I help you today?"
        )

    @app.event("message")
    def message(event, client: WebClient):
        """Handles the message event: https://api.slack.com/events/message.im"""
        client.chat_postMessage(
            channel=event["channel"], 
            thread_ts=event["thread_ts"],
            text=f"<@{event["user"]}> said: '{event["text"]}'"
        )
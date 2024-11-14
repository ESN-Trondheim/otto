from commands import commands

from .helpers import actions, blocks, button, section

welcome_message_buttons = ", ".join(
    [button(command.keyword, command.keyword) for command in commands.values()]
)
welcome_message_blocks = [{
    "type": "section",
    "text": { 
        "type": "plain_text",
        "text": "Hey :wave: What would you like to do today?"
        "emoji": True
    }
}]

blocks(
    [
        section("Hey :wave: What would you like to do today?"),
        actions([welcome_message_buttons]),
    ]
)



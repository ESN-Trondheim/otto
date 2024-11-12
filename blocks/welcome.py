from helpers import actions, blocks, button, section

from commands import commands

welcome_message_buttons = ", ".join(
    [button(command.keyword, command.keyword) for command in commands]
)
welcome_message_blocks = blocks(
    [
        section("Hey :wave: What would you like to do today?"),
        actions([welcome_message_buttons]),
    ]
)

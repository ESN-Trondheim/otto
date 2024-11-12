from commands import commands

from helpers import blocks, section, actions, button


welcome_message_buttons = ", ".join([button(command.keyword, command.keyword) for command in commands])
welcome_message_blocks = blocks([
    section("Hey :wave: What would you like to do today?"),
    actions([welcome_message_buttons])
])
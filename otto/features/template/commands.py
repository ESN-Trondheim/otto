from slack_bolt import Args

from otto.command import command


@command(
    "keyword",
    "Description of the command.",
)
def template_command(args: Args):
    """Docstring that describes this command"""
    pass

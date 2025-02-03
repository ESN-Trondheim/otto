from slack_bolt import Args

from otto.app import app


@app.action("action_id")
def template_action(args: Args):
    """Docstring that describes this action"""
    pass

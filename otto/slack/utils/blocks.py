def section(text: str):
    return {
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": text,
            "emoji": True,
        },
    }


def text_input(text: str, value: str):
    return {
        "type": "input",
        "dispatch_action": False,
        "element": {
            "type": "plain_text_input",
            "action_id": value,
        },
        "label": {"type": "plain_text", "text": text, "emoji": True},
    }


def select_input(text: str, value: str, options: list[str], initial_option: str = None):
    d = {
        "type": "input",
        "dispatch_action": False,
        "element": {
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select an option",
                "emoji": True,
            },
            "options": [
                {
                    "text": {"type": "plain_text", "text": option, "emoji": True},
                    "value": option,
                }
                for option in options
            ],
            "action_id": value,
        },
        "label": {"type": "plain_text", "text": text, "emoji": True},
    }

    if initial_option is not None:
        d["element"]["initial_option"] = {
            "text": {
                "type": "plain_text",
                "text": initial_option if initial_option else options[0],
                "emoji": True,
            },
            "value": initial_option if initial_option else options[0],
        }

    return d


def date_input(text: str, value: str):
    return {
        "type": "input",
        "element": {
            "type": "datepicker",
            "placeholder": {
                "type": "plain_text",
                "text": "Select a date",
                "emoji": True,
            },
            "action_id": value,
        },
        "label": {"type": "plain_text", "text": text, "emoji": True},
    }


def actions(elements: list[dict[str, any]]):
    return {"type": "actions", "elements": elements}


def button(
    action_id: str, text: str, value: str = None, style: str = "default"
) -> dict:
    return {
        "type": "button",
        "text": {"type": "plain_text", "text": text, "emoji": True},
        "action_id": action_id,
        "value": value if value else action_id,
        "style": style,
    }

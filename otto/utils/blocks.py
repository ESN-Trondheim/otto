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
        "element": {
            "type": "plain_text_input",
            "action_id": value
        },
        "label": {
			"type": "plain_text",
			"text": text,
			"emoji": True
		}
    }


def select_input(text: str, value: str, options: list[str]):
    return {
        "type": "input",
        "element": {
            "type": "static_select",
			"placeholder": {
				"type": "plain_text",
				"text": "Select an option",
				"emoji": True
			},
            "options": [
                {
                    "text": {
						"type": "plain_text",
						"text": option,
						"emoji": True
					},
					"value": option
                }
                for option in options
            ],
            "action_id": value
        },
        "label": {
			"type": "plain_text",
			"text": text,
			"emoji": True
		}
    }

def actions(elements: list[dict[str, any]]):
    return {"type": "actions", "elements": elements}


def button(text: str, value: str) -> dict:
    return {
        "type": "button",
        "text": {"type": "plain_text", "text": text, "emoji": True},
        "value": value,
        "action_id": value,
    }

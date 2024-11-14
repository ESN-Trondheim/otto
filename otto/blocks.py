def section(text: str):
    return {
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": text,
            "emoji": True,
        },
    }

def actions(elements: list[dict[str, any]]):
    return {
        "type": "actions",
        "elements": elements
    }

def button(text: str, value: str) -> dict:
    return {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": text,
            "emoji": True
        },
        "value": value,
        "action_id": value
    }
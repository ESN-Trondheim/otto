blocks = lambda elements: """
    {{
        "blocks": [{0}]
    }}
""".format(", ".join(elements))

section = lambda text: """
    {{
		"type": "section",
		"text": {{
			"type": "plain_text",
			"text": "{0}",
			"emoji": true
		}}
	}}
""".format(text)

actions = lambda elements: """
    {{
        "type": "actions",
        "elements": [{0}]
    }}
""".format(", ".join(elements))

button = lambda text, value: """
    {{
        "type": "button",
        "text": {{
            "type": "plain_text",
            "text": "{0}",
            "emoji": true
        }},
        "value": "{1}",
        "action_id": "{1}"
    }}
""".format(text, value)
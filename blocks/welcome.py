from commands import commands


buttons = ", ".join(
    [
        f"""
            {{
                "type": "button",
                "text": {{
                    "type": "plain_text",
                    "text": "{command.keyword}",
                    "emoji": true
                }},
                "value": "{command.keyword}",
                "action_id": "{command.keyword}"
            }}
        """
        for command in commands.values()
    ]
)


welcome_blocks = f"""{{
        "blocks": [
            {{
                "type": "section",
                "text": {{
                    "type": "plain_text",
                    "text": "Hey :wave: What would you like to do today?",
                    "emoji": true
                }}
            }},
            {{
                "type": "actions",
                "elements": [
                   {buttons}
                ]
            }}
        ]
}}
"""

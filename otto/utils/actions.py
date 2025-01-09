def transform_action_state_values(values: dict):
    output_dict = {}

    for field in values.values():
        for key, value in field.items():
            if value["type"] == "static_select":
                text = value["selected_option"]["value"]
            else:
                text = value["value"]

            output_dict[key] = text

    return output_dict

import json


def get_config():
    with open("config/config.json") as config:
        config = json.loads(config.read())
        return config


def update_config(new_config):
    current_config = get_config()

    for key, value in new_config.items():
        if key in current_config:
            if isinstance(current_config[key], type(value)):
                current_config[key] = value
            else:
                raise ValueError(
                    f"Invalid value type for key '{key}'. Expected {type(current_config[key])}, but got {type(value)}."
                )

    with open("config/config.json", "w") as config:
        config.write(json.dumps(current_config, indent=4))

    return

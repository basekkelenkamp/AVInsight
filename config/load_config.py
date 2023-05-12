import json


def get_config():
    with open("config/config.json") as config:
        config = json.loads(config.read())
        return config


def update_config(new_config):

    for key in new_config:
        new_config[key] = [dict(t) for t in set(tuple(d.items()) for d in new_config[key])]

    for outer_key, outer_value in new_config.items():
        for inner_dict in outer_value:
            for key, value in inner_dict.items():
                if isinstance(value, bool):
                    inner_dict[key] = str(value).lower()

    with open("config/config.json", "w") as config:
        config.write(json.dumps(new_config, indent=4, sort_keys=True))

    return

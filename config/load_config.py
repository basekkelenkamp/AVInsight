import json


class Config:
    def __init__(
        self,
        clear_archive_after_days: int,
        enable_archive: str,
        disk: str,
        interval: float,
    ):
        self.clear_archive_after_days = clear_archive_after_days
        self.enable_archive = enable_archive == "true"
        self.disk = disk
        self.interval = interval

    def update(self, interval, disk, enable_archive, clear_archive_days):
        self.interval = interval
        self.disk = disk
        self.enable_archive = enable_archive
        self.clear_archive_days = clear_archive_days

    def get_params(self):
        return self.interval, self.disk, self.enable_archive, self.clear_archive_days


def get_config(no_object: bool = False):
    with open("config/config.json") as config:
        config = json.loads(config.read())
        if no_object:
            return config

        params = {}
        for li in config.values():
            for metric in li:
                for k, v in metric.items():
                    params[k] = v

        return Config(**params)


def update_config(new_config):
    for key in new_config:
        new_config[key] = [
            dict(t) for t in set(tuple(d.items()) for d in new_config[key])
        ]

    for outer_key, outer_value in new_config.items():
        for inner_dict in outer_value:
            for key, value in inner_dict.items():
                if isinstance(value, bool):
                    inner_dict[key] = str(value).lower()

    breakpoint()
    with open("config/config.json", "w") as config:
        config.write(json.dumps(new_config, indent=4, sort_keys=True))

    return

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class Setting:
    name: str
    value: Any
    description: str


@dataclass
class Config:
    settings: List[Setting]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        settings = [Setting(**item) for sublist in data.values() for item in sublist]
        return cls(settings)

    def to_dict(self) -> Dict[str, Any]:
        archive_settings = [asdict(setting) for setting in self.settings if setting.name.startswith('archive')]
        metrics_settings = [asdict(setting) for setting in self.settings if not setting.name.startswith('archive')]
        return {'archive-settings': archive_settings, 'metrics-settings': metrics_settings}

    def get_setting_values(self) -> Dict[str, Any]:
        return {setting.name: setting.value for setting in self.settings}

    def get_setting_value(self, name: str) -> Any:
        for setting in self.settings:
            if setting.name == name:
                return setting.value
        raise ValueError(f"No setting found with name '{name}'")


def get_config():
    with open("config/config.json") as f:
        data = json.load(f)
        return Config.from_dict(data)


def update_config(new_config):
    breakpoint()
    for key in new_config:
        new_config[key] = [
            dict(t) for t in set(tuple(d.items()) for d in new_config[key])
        ]

    for outer_key, outer_value in new_config.items():
        for inner_dict in outer_value:
            for key, value in inner_dict.items():
                if isinstance(value, bool):
                    inner_dict[key] = str(value).lower()

    with open("config/config.json", "w") as config:
        config.write(json.dumps(new_config, indent=4, sort_keys=True))

    return

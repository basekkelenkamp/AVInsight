import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class Setting:
    name: str
    value: Any
    description: str
    category: str
    datatype: str


@dataclass
class Config:
    settings: List[Setting]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        settings = [Setting(**item) for sublist in data.values() for item in sublist]
        return cls(settings)

    def to_dict(self) -> Dict[str, Any]:
        categories = {setting.category for setting in self.settings}
        return {
            category: [asdict(setting) for setting in self.settings if setting.category == category]
            for category in categories
        }

    def get_setting_values(self) -> Dict[str, Any]:
        return {setting.name: setting.value for setting in self.settings}

    def get_setting_value(self, name: str) -> Any:
        for setting in self.settings:
            if setting.name == name:
                if setting.value == "true":
                    return True
                elif setting.value == "false":
                    return False
                return setting.value
        raise ValueError(f"No setting found with name '{name}'")


def get_config():
    with open("config/config.json") as f:
        data = json.load(f)
        return Config.from_dict(data)


def update_config(new_config):
    with open("config/config.json", "w") as config:
        config.write(json.dumps(new_config, indent=4, sort_keys=False))
    return

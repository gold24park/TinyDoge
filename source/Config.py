import os.path

import yaml

from Paths import getRootPath


class Config:

    def __init__(self):
        self.config_path = os.path.join(getRootPath(), 'tinydoge-config.yaml')
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w+') as f:
                self.conf = dict(
                    recent_path="",
                    avg_quality=80
                )
                yaml.dump(self.conf, f)
        else:
            with open(self.config_path, 'r') as f:
                self.conf = yaml.safe_load(f)

    def get(self, key: str, default_value):
        return self.conf.get(key, default_value)

    def set(self, key: str, value):
        self.conf[key] = value
        with open(self.config_path, 'w') as f:
            yaml.dump(self.conf, f)







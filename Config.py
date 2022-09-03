import os.path

import yaml


class Config:

    def __init__(self):
        if not os.path.exists('config.yaml'):
            with open('config.yaml', 'w+') as f:
                self.conf = dict(
                    recent_path="",
                    avg_quality=80
                )
                yaml.dump(self.conf, f)
        else:
            with open('config.yaml') as f:
                self.conf = yaml.safe_load(f)

    def get(self, key: str, default_value):
        return self.conf.get(key, default_value)

    def set(self, key: str, value):
        self.conf[key] = value
        with open('config.yaml', 'w') as f:
            yaml.dump(self.conf, f)




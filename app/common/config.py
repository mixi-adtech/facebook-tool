import json, os

class Config:
    def __init__(self):
        self.set_config()

    def set_config(self):
        this_dir = os.path.dirname(__file__)
        config_filename = os.path.join(this_dir, '../../config/config.json')
        config_file = open(config_filename)
        config = json.load(config_file)
        config_file.close()
        self.config = config

    def get_config(self):
        return self.config

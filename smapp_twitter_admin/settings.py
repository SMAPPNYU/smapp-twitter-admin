import os
import yaml
from smapp_twitter_admin import app

settings_path = os.path.realpath(os.path.join(os.path.dirname(__file__), 'settings.yaml'))
with open(settings_path) as settings_file:
    app_settings = yaml.load(settings_file)
if app_settings:
    for key in app_settings:
        app.config[key] = app_settings[key]

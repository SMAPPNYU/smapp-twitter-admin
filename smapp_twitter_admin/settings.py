from smapp_twitter_admin import app

with open('settings.yaml') as settings_file:
    app_settings = yaml.load(settings_file)
for key in app_settings:
    app.config[key] = app_settings[key]
import matplotlib
matplotlib.use('Agg')

from flask import Flask
app = Flask(__name__)

import smapp_twitter_admin.settings
import smapp_twitter_admin.oauth_module
import smapp_twitter_admin.authorization_module
import smapp_twitter_admin.views
import smapp_twitter_admin.models

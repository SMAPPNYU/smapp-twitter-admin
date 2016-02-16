killall gunicorn
/home/smapp/.venvs/smapp-twitter-admin/bin/gunicorn smapp_twitter_admin:app -b unix:/tmp/gunicorn_flask.sock -w 4 -t 120 -D --access-logfile gunicorn_access_log.log --error-logfile gunicorn_error_log.log

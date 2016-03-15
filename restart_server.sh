killall gunicorn
/home/yvan/miniconda3/envs/smapp-twitter-admin/bin/gunicorn smapp_twitter_admin:app -b unix:/tmp/gunicorn_flask.sock -w 4 -t 120 -D --access-logfile logs/gunicorn/gunicorn_access_log.log --error-logfile logs/gunicorn/gunicorn_error_log.log

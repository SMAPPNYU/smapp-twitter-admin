# smapp lab admin app for twitter collections

This is a flask app to manage twitter collections

* manage search terms for collections
* display summary statistics about collections
* future hope: start/stop collections

To run the server normally or restart it run:

```sh
bash restart_server.sh
```

or just run
```sh

killall gunicorn

/home/smapp/.venvs/smapp-twitter-admin/bin/gunicorn smapp_twitter_admin:app -b unix:/tmp/gunicorn_flask.sock -w 4 -t 120 -D --access-logfile gunicorn_access_log.log --error-logfile gunicorn_error_log.log

``` 

To find an internal server error, run:
```sh
source /home/smapp/.venvs/smapp-twitter-admin/bin/activate

python runserver.py # where debug is set to true in app.run
```

Then go to port 5000/ of whatever server/ip is running the flask app.
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

/home/smapp/.venvs/smapp-twitter-admin/bin/gunicorn smapp_twitter_admin:app -b 127.0.0.1:8000 -w 4 -t 120 -D --access-logfile gunicorn_access_log.log --error-logfile gunicorn_error_log.log
``` 

ALSO:
make sure to have a tunnel to db.

To find an internal server error, run:
```sh
source /home/smapp/.venvs/smapp-twitter-admin/bin/activate

python runserver.py # where debug is set to true in app.run
```

Then go to port 5000/ of whatever server/ip is running the flask app.

Settings file structure:

```yaml
SECRET_KEY: 1234567890

TWITTER:
    consumer_key: my_secret_consumer_key
    consumer_secret: my_consumer_secret
    
individualdb:
    host: localhost
    port: 27017
    username: username
    password: password

authdb:
    host: localhost
    port: 27017
    username: username
    password: password

collection-name-exceptions:
    PostCommunist:
        tweets: russia_tweets
        filter-criteria: 'russia_tweets_filter_criteria'
    test:
        filter-criteria: 'test_tweets_filter_criteria'
```

SECRET_KEY - no idea what it does
TWITTER - twitter app info to allow twitter login to dashboard
authdb - authentication database credentials
individualdb - auth details for each individual db
collection-name-exceptions - no idea

The way the flask app works is that in models.py it authenticates once to the admin db. then it authenticates to each individual db.

We need credentials for both. Before they shared the same credentials, now they have different ones. (admin vs non admin)

resources:

How to setup nginx and gunicorn on a new server:

http://blog.marksteve.com/deploy-a-flask-application-inside-a-digitalocean-droplet

how to setup nginx and sockets:

http://stackoverflow.com/questions/13660118/running-a-flask-app-with-nginx-and-gunicorn

how to uninstall and reset nginx if you mess up your installation:

http://stackoverflow.com/questions/12362967/how-can-i-restore-etc-nginx
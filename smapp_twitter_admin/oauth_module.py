from flask import g, session, request, url_for, flash
from flask import redirect
from flask_oauthlib.client import OAuth
from smapp_twitter_admin import app

oauth = OAuth(app)

twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    app_key='TWITTER'
)

@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']

@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']

@app.route('/login')
def login():
    print("hahaha")
    callback_url = url_for('.oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('welcome_view'))

@app.route('/oauthorized')
@twitter.authorized_handler
def oauthorized(resp):
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('welcome_view'))

def current_user():
    if 'twitter_oauth' in session:
        return session.get('twitter_oauth').get('screen_name')
    else:
        return None
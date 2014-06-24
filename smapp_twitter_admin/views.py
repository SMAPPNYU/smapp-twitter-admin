from smapp_twitter_admin import app
from smapp_twitter_admin.models import Permission
from smapp_twitter_admin.oauth_module import current_user
from smapp_twitter_admin.models import Permission
from flask import session, render_template, redirect, request

@app.before_request
def user_login_check():
    if not request.path in ['/', '/login', '/oauthorized']:
        print current_user()
        if current_user():
            return
        return redirect('/')

@app.route('/')
def welcome_view():
    if 'twitter_oauth' in session:
        return redirect('/dashboard')
    else:
        return render_template('welcome.html')

@app.route('/dashboard')
def dashboard():
    collections = [p['collection_name'] for p in Permission.all()]
    return render_template('dashboard.html', collections=collections)

@app.route('/collections/<collection_name>')
def collections(collection_name):
    filter_criteria = Permission.find('collection_name')
    import IPython
    IPython.embed()

    return "hello %s" % collection_name

@app.route('/filter-criteria')
def filter_criteria_index():
    return render_template('filter-criteria/index.html')
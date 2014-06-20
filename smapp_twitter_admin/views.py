from smapp_twitter_admin import app
from smapp_twitter_admin.oauth_module import current_user
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
    return render_template('dashboard.html')

@app.route('/filter-criteria')
def filter_criteria_index():
    return render_template('filter-criteria/index.html')
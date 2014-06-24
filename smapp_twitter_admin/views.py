from smapp_twitter_admin import app
from smapp_twitter_admin.models import Permission, FilterCriteria, Tweet
from smapp_twitter_admin.oauth_module import current_user
from smapp_twitter_admin.models import Permission
from flask import _request_ctx_stack, session, render_template, redirect, request

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
    filter_criteria = FilterCriteria.find_by_collection_name(collection_name)
    latest_tweets = Tweet.latest_for(collection_name)
    count = Tweet.count(collection_name)

    return render_template('collections/show.html', collection_name=collection_name,
                                                    filter_criteria=filter_criteria,
                                                    latest_tweets=latest_tweets,
                                                    count=count)

@app.route('/filter-criteria')
def filter_criteria_index():
    return render_template('filter-criteria/index.html')

@app.route('/filter-criteria/<collection_name>/<id>', methods=['GET'])
def filter_criteria_show(collection_name, id):
    filter_criteria = FilterCriteria.find_by_collection_name_and_object_id(collection_name, id)
    return render_template('filter-criteria/edit.html', filter_criteria=filter_criteria)

@app.route('/filter-criteria/<collection_name>/<id>', methods=['POST'])
def filter_criteria_edit(collection_name, id):
    return "edit fc"

@app.route('/filter-criteria/delete/<collection_name>/<id>', methods=['post'])
def filter_criteria_delete(collection_name, id):
    return "delete fc"
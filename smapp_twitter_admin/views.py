from smapp_twitter_admin import app
from smapp_twitter_admin.models import Permission, FilterCriteria, Tweet, LimitMessage
from smapp_twitter_admin.oauth_module import current_user
from smapp_twitter_admin.forms import FilterCriterionForm, FilterCriteriaManyForm
from flask import _request_ctx_stack, session, render_template, redirect, request, url_for, send_file, abort
from datetime import datetime, timedelta

import smapp_twitter_admin.graphing as graphing
from smapp_twitter_admin.authorization_module import EditTwitterCollectionPermission

@app.before_request
def user_login_check():
    if not request.path in ['/', '/login', '/oauthorized']:
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
    collections = sorted([p['collection_name'] for p in Permission.all()])
    return render_template('dashboard.html', collections=collections)

@app.route('/collections/<collection_name>')
def collections(collection_name):
    filter_criteria = FilterCriteria.find_by_collection_name(collection_name)
    latest_tweets = Tweet.latest(collection_name, 5)[-5:]
    count = Tweet.count(collection_name)

    return render_template('collections/show.html', collection_name=collection_name,
                                                    filter_criteria=filter_criteria,
                                                    latest_tweets=latest_tweets,
                                                    count=count,
                                                    can_edit=EditTwitterCollectionPermission(collection_name).can())

@app.route('/collections/<collection_name>/graphs/<graph_name>')
def collection_graph(collection_name, graph_name):
    if graph_name == 'tpm':
        objects = Tweet.since(collection_name, datetime.utcnow()-timedelta(hours=1), n=50000)
        graph_method = graphing.tpm_plot
    elif graph_name == 'limits':
        objects = list(LimitMessage.all_for(collection_name))
        graph_method = graphing.limits_plot
    if len(objects) > 0:
        graph = graph_method(objects)
        response = send_file(graph, as_attachment=False, attachment_filename='grph.svg', cache_timeout=0)
    else: response = 'no objects', 404

    return response

@app.route('/filter-criteria/<collection_name>/new-many', methods=['GET'])
def filter_criteria_new_many(collection_name):
    # form = FilterCriterionForm(active=True, date_added=datetime.now())
    # return render_template('filter-criteria/new.html', form=form, collection_name=collection_name)
    form = FilterCriteriaManyForm()
    return render_template('filter-criteria/new-many.html', form=form, collection_name=collection_name)

@app.route('/filter-criteria/<collection_name>/create-many', methods=['POST'])
def filter_criteria_create_many(collection_name):
    if not EditTwitterCollectionPermission(collection_name).can():
        abort(403)

    form = FilterCriteriaManyForm(request.form)
    if form.validate():
        keywords = filter(None,[keyword.strip() for keyword in form.keywords.data.split('\n')])
        for keyword in keywords:
            FilterCriteria.create(collection_name, {'active': True, 'date_added': datetime.now(), "date_removed": None, 'filter_type': 'track', 'value': keyword})
        return redirect(url_for('collections', collection_name=collection_name))
    else:
        return render_template('filter-criteria/new-many.html')


@app.route('/filter-criteria/<collection_name>/new', methods=['GET'])
def filter_criteria_new(collection_name):
    form = FilterCriterionForm(active=True, date_added=datetime.now(), date_removed=None)
    return render_template('filter-criteria/new.html', form=form, collection_name=collection_name)

@app.route('/filter-criteria/<collection_name>/create', methods=['POST'])
def filter_criteria_create(collection_name):
    if not EditTwitterCollectionPermission(collection_name).can():
        abort(403)

    form = FilterCriterionForm(request.form)
    if form.validate():
        form.date_added.data = datetime.combine(form.data['date_added'], datetime.min.time())
        if form.date_removed.data:
            form.date_removed.data = datetime.combine(form.data['date_removed'], datetime.min.time())
        FilterCriteria.create(collection_name, form.data)
        return redirect(url_for('collections', collection_name=collection_name))
    else:
        return render_template('filter-criteria/new.html', form=form)

@app.route('/filter-criteria/<collection_name>/<id>', methods=['GET'])
def filter_criteria_edit(collection_name, id):
    filter_criterion = FilterCriteria.find_by_collection_name_and_object_id(collection_name, id)
    form = FilterCriterionForm(**filter_criterion)
    return render_template('filter-criteria/edit.html', form=form, collection_name=collection_name, id=id)

@app.route('/filter-criteria/<collection_name>/<id>', methods=['POST'])
def filter_criteria_update(collection_name, id):
    if not EditTwitterCollectionPermission(collection_name).can():
        abort(403)

    form = FilterCriterionForm(request.form)
    if form.validate():
        form.date_added.data = datetime.combine(form.data['date_added'], datetime.min.time())
        if form.date_removed.data:
            form.date_removed.data = datetime.combine(form.data['date_removed'], datetime.min.time())
        FilterCriteria.update(collection_name, id, form.data)
        return redirect(url_for('collections', collection_name=collection_name))
    else:
        return redirect(url_for('filter_criteria_edit', collection_name=collection_name, id=id))

@app.route('/filter-criteria/delete/<collection_name>/<id>', methods=['POST'])
def filter_criteria_delete(collection_name, id):
    if not EditTwitterCollectionPermission(collection_name).can():
        abort(403)

    FilterCriteria.delete(collection_name, id)
    return redirect(url_for('collections', collection_name=collection_name))

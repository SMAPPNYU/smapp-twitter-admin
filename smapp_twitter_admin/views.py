import bson.json_util as json
from smapp_twitter_admin import app
from smapp_twitter_admin.models import Permission, FilterCriteria, Tweet, LimitMessage, PostFilter, ThrowawayMessage, CollectionStats
from smapp_twitter_admin.oauth_module import current_user
from smapp_twitter_admin.forms import FilterCriterionForm, FilterCriteriaManyForm, PostFilterForm, PermissionForm
from smapp_twitter_admin.post_filters import filter_docstring
from flask import _request_ctx_stack, session, render_template, redirect, request, url_for, send_file, abort
from datetime import datetime, timedelta
from werkzeug.contrib.cache import SimpleCache

import smapp_twitter_admin.graphing as graphing
from smapp_twitter_admin.authorization_module import EditTwitterCollectionPermission, admin_permission


cache = SimpleCache()

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
@admin_permission.require(http_exception=403)
def dashboard():
    collections, collections_active = get_cached_collection_list()

    return render_template('dashboard.html', active_collections = [collections[i] for i,a in enumerate(collections_active) if a],
                                             inactive_collections = [collections[i] for i,a in enumerate(collections_active) if not a])


@app.route('/collections/<collection_name>')
@admin_permission.require(http_exception=403)
def collections(collection_name):
    filter_criteria = list(FilterCriteria.find_by_collection_name(collection_name))
    latest_tweets = Tweet.latest(collection_name, 5)[-5:]
    count = Tweet.count(collection_name)
    post_filters = PostFilter.all_for(collection_name)
    permissions = Permission.all_for(collection_name)
    show_map_link = any(fc['filter_type'] == 'geo' for fc in filter_criteria)

    return render_template('collections/show.html', collection_name=collection_name,
                                                    filter_criteria=filter_criteria,
                                                    latest_tweets=latest_tweets,
                                                    count=count,
                                                    post_filters=post_filters,
                                                    permissions=permissions,
                                                    default_start_time_histogram=(datetime.utcnow()-timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'),
                                                    default_end_time_histogram=datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                                                    show_map_link=show_map_link,
                                                    can_edit=EditTwitterCollectionPermission(collection_name).can())

@app.route('/collections/<collection_name>/graphs/<graph_name>')
def collection_graph(collection_name, graph_name):
    explode = False
    if graph_name == 'tpm':
        args = (Tweet._collection_for(collection_name), request.args['start_datetime'], request.args['end_datetime'])
        explode = True
        graph_method = graphing.tpm_plot
    elif graph_name == 'limits':
        args = list(LimitMessage.all_for(collection_name))
        graph_method = graphing.limits_plot
    elif graph_name == 'throwaway':
        args = list(ThrowawayMessage.latest_for(collection_name))
        graph_method = graphing.throwaway_plot
    if args:
        graph = graph_method(*args) if explode else graph_method(args)
        response = send_file(graph, as_attachment=False, attachment_filename='grph.svg', cache_timeout=0)
    else: response = 'no objects', 404

    return response

@app.route('/filter-criteria/<collection_name>/new-many', methods=['GET'])
def filter_criteria_new_many(collection_name):
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
        return redirect(url_for('collections', collection_name=collection_name) + '#filter-criteria')
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
        return redirect(url_for('collections', collection_name=collection_name) + '#filter-criteria')
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
        return redirect(url_for('collections', collection_name=collection_name) + '#filter-criteria')
    else:
        return redirect(url_for('filter_criteria_edit', collection_name=collection_name, id=id))

@app.route('/filter-criteria/delete/<collection_name>/<id>', methods=['POST'])
def filter_criteria_delete(collection_name, id):
    if not EditTwitterCollectionPermission(collection_name).can():
        abort(403)

    FilterCriteria.delete(collection_name, id)
    return redirect(url_for('collections', collection_name=collection_name) + '#filter-criteria')

@app.route('/filter-criteria/<collection_name>/map', methods=['GET'])
def geo_filters_map(collection_name):
    filter_criteria = [fc for fc in FilterCriteria.find_by_collection_name(collection_name) if fc['filter_type'] == 'geo']
    boxes = [[float(e) for e in fc['value']] for fc in filter_criteria]

    return render_template('map/map.html', boxes=boxes)


@app.route('/post-filters/<collection_name>/new', methods=['GET'])
def post_filter_new(collection_name):
    form = PostFilterForm(active=True, date_added=datetime.now())
    return render_template('post-filters/new.html', form=form, collection_name=collection_name)

@app.route('/post-filters/<collection_name>/create', methods=['POST'])
def post_filter_create(collection_name):
    if not EditTwitterCollectionPermission(collection_name).can():
        abort(403)

    form = PostFilterForm(request.form)
    if form.validate():
        form.date_added.data = datetime.combine(form.data['date_added'], datetime.min.time())
        if form.date_removed.data:
            form.date_removed.data = datetime.combine(form.data['date_removed'], datetime.min.time())
        PostFilter.create(collection_name, form.data)
        return redirect(url_for('collections', collection_name=collection_name) + '#post-filtering')
    else:
        return render_template('post-filters/new.html', form=form)

@app.route('/post-filters/<collection_name>/<id>', methods=['GET'])
def post_filter_edit(collection_name, id):
    filter_criterion = PostFilter.find_by_collection_name_and_object_id(collection_name, id)
    form = PostFilterForm(**filter_criterion)
    return render_template('post-filters/edit.html', form=form, collection_name=collection_name, id=id)

@app.route('/post-filters/<collection_name>/<id>', methods=['POST'])
def post_filter_update(collection_name, id):
    if not EditTwitterCollectionPermission(collection_name).can():
        abort(403)

    form = PostFilterForm(request.form)
    if form.validate():
        form.date_added.data = datetime.combine(form.data['date_added'], datetime.min.time())
        if form.date_removed.data:
            form.date_removed.data = datetime.combine(form.data['date_removed'], datetime.min.time())
        PostFilter.update(collection_name, id, form.data)
        return redirect(url_for('collections', collection_name=collection_name) + '#post-filtering')
    else:
        return redirect(url_for('post_filter_edit', collection_name=collection_name, id=id))

@app.route('/post-filters/delete/<collection_name>/<id>', methods=['POST'])
def post_filter_delete(collection_name, id):
    if not EditTwitterCollectionPermission(collection_name).can():
        abort(403)

    PostFilter.delete(collection_name, id)
    return redirect(url_for('collections', collection_name=collection_name) + '#post-filtering')

@app.route('/post-filter-docstring/<fname>', methods=['GET'])
def post_filter_docstring(fname):
    return filter_docstring(fname)

@app.route('/permissions/<collection_name>/new')
def permission_new(collection_name):
    form = PermissionForm()
    return render_template('permissions/new.html', form=form, collection_name=collection_name)

@app.route('/permissions/<collection_name>/create', methods=['POST'])
def permission_create(collection_name):
    if not EditTwitterCollectionPermission(collection_name).can():
        abort(403)
    form = PermissionForm(request.form)
    if form.validate():
        Permission.create(collection_name, form.data['twitter_handle'])
        return redirect(url_for('collections', collection_name=collection_name) + '#permissions')
    else:
        return render_template('permissions/new.html', form=form, collection_name=collection_name)

@app.route('/permissions/delete/<collection_name>/<twitter_handle>', methods=['POST'])
def permission_delete(collection_name, twitter_handle):
    if not EditTwitterCollectionPermission(collection_name).can():
        abort(403)

    Permission.delete(collection_name, twitter_handle)
    return redirect(url_for('collections', collection_name=collection_name) + '#permissions')

@app.route('/collections/<collection_name>/stats')
def collection_stats(collection_name):
    filter_criteria = {str(fc['_id']): fc for fc in FilterCriteria.find_by_collection_name(collection_name)}
    stats = CollectionStats.all_since(collection_name, datetime.utcnow()-timedelta(weeks=4))
    return json.dumps({'filter-criteria': filter_criteria, 'stats': stats})

@app.errorhandler(403)
def permission_denied(e):
    return "@{} not authorized.".format(current_user())

def get_cached_collection_list():
    ret = cache.get('collection-list')
    if ret is None:
        one_hr_ago = datetime.utcnow() - timedelta(hours=1)
        collections = sorted([p['collection_name'] for p in Permission.all()])
        collections_active = [False for c in collections]
        for i,c in enumerate(collections):
            if c in ['DebateSpain', 'ItalianTweets', 'SOTU', 'USElection']:
                continue
            try:
                tweets = Tweet.latest(c,1)
            except TypeError:
                continue
            try:
                collections_active[i] = tweets[0]['timestamp'] > one_hr_ago
            except IndexError:
                continue
        ret = (collections, collections_active)
        cache.set('collection-list', ret, timeout=10*60)
    return ret
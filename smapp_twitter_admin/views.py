from smapp_twitter_admin import app

@app.route('/')
def welcome_view():
    if 'twitter_oauth' in session:
        return redirect('/admin')
    else:
        return render_template('welcome.html')
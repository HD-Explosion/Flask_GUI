from app import app
from flask import render_template
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for


@app.route('/')
@app.route('/index')

def index():
    user = {'username': 'Xiaohe'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/ui')
def ui():
    return render_template('ui.html')


@app.route('/error')
def error():
    return render_template('error.html')
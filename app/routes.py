from app import app, db, login
from app.models import User, Search
from app.forms import LoginForm, RegistrationForm
from app.custom import require_role
from werkzeug.urls import url_parse
from flask import render_template, redirect, url_for, flash, request, jsonify, abort, send_file
from flask_login import current_user, login_user, logout_user, login_required
from multiprocessing import Value
import flask
import requests
import xmltodict
import random
import string
import faker
import json
import pprint
import os
import sys

print = pprint.PrettyPrinter().pprint
fake = faker.Faker()
strgen = lambda length, charset=string.ascii_letters, weights=None : ''.join(random.choices(list(charset), k=length, weights=weights))

@app.route('/', subdomain='api')
def api_index():
    return "api"

@app.route('/time/')
def time():
    value = request.args.get('value')
    if not value:
        return '<br>'.join(['[int] value', '[int list] lengths', '[string list] strings', '[boolean] reverse', '[string] pluralappend', '[boolean] synonym'])
    value = int(value)
    lengths = request.args.get('lengths')
    if lengths: lengths = lengths.split(',')
    strings = request.args.get('strings')
    if strings: strings = strings.split(',')
    if (len(lengths or []) + len(strings or []) > 0) and (len(lengths or []) + 1 != len(strings or [])):
        return f'error: lengths ({len(lengths or [])}) and strings ({len(strings or [])}) arrays must be same length to process properly'
    if lengths: lengths = list(map(int, lengths))
    reverse = request.args.get('reverse')
    if reverse: reverse = bool(reverse)
    return timeformat(value=value, lengths=lengths or [60, 60, 24, 365], strings=strings or ['second', 'minute', 'hour', 'day', 'year'], reverse=True if reverse is None else reverse)

def timeformat(value, lengths=[60, 60, 24, 365], strings=['second', 'minute', 'hour', 'day', 'year'], reverse=True, pluralappend='s', synonym=False):
    converted = [value]
    for index, length in enumerate(lengths):
        temp = converted[-1] // length
        if not synonym:
            converted[-1] = converted[-1] % length
        if temp != 0:
            converted.append(temp)
        else:
            break    
    strings = strings[:len(converted)]
    build = ['{} {}'.format(value, strings[i] + pluralappend if value > 1 or value == 0 else strings[i]) for i, value in enumerate(converted)][::-1]
    build = ', '.join(build)
    return build

@app.route('/avatar/')
@app.route('/avatar/<id>/')
@app.route('/avatar/<id>')
def getAvatar(id=''):
    # Constants
    headers = {'Authorization' : f'Bot {app.config["DISCORD_TOKEN"]}'}
    api = "https://discordapp.com/api/v6/users/{}"
    cdn = "https://cdn.discordapp.com/avatars/{}/{}.png"
    # Get User Data which contains Avatar Hash
    response = requests.get(api.format(id), headers=headers)
    if response.status_code != 200:
        return response.text
    user = json.loads(response.text)
    url = cdn.format(id, user['avatar'])
    return "<img src=\"{}\">".format(url)

@app.route('/userinfo/')
@login_required
@require_role(roles=['Admin'])
def user_info():
    prepare = {
        'id' : current_user.get_id(),
        'email' : current_user.email,
        'username' : current_user.username,
        'password_hash' : current_user.password_hash,
        'is_active' : current_user.is_active,
        'is_anonymous' : current_user.is_anonymous,
        'is_authenticated' : current_user.is_authenticated,
        'metadata' : current_user.metadata.info,
        'uroles' : current_user.get_roles()
    }
    return jsonify(prepare)



@app.route('/')
def index():
    jobs = [
        'Student Photographer',
        'Highschool Student',
        'Web Developer',
        'Python Developer',
        'Software Engineer',
    ]
    return render_template('index.html', content=content, job=random.choice(jobs))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registered Successfully!', 'info')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, hideRegister=True)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form, hideLogin=True)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))
from app import app
from app.models import User
from app.forms import LoginForm
from werkzeug.urls import url_parse
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
import requests
import xmltodict
import base64
import random
import string
import faker
import json

fake = faker.Faker()

def strgen(length): return ''.join(random.choices(list(string.ascii_letters), k=length))

@app.route('/api')
def api():
    return 'fuckoff'

@app.route('/dashboard')
def dashboard():
    return ''

@app.route('/userinfo')
@login_required
def user_info():
    prepare = {
        'id' : current_user.get_id(),
        'email' : current_user.email,
        'username' : current_user.username,
        'password_hash' : current_user.password_hash,
        'is_active' : current_user.is_active,
        'is_anonymous' : current_user.is_anonymous,
        'is_authenticated' : current_user.is_authenticated,
        'metadata' : current_user.metadata.info
    }
    return jsonify(prepare)

@app.route('/')
def index():
    if current_user.is_authenticated:
        print(current_user)
    content = [{'text': fake.paragraph(nb_sentences=15),
                'seed': random.randint(0, 1000),
                'title': fake.word().title()}
               for _ in range(10)]
    return render_template('index.html', content=content)

@app.route('/signup')
@app.route('/sign-up')
def signup():
    return render_template('signup.html', title='Sign Up', hideSignup=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, hideLogin=True)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def boolparse(string, default=False):
    # falses = ['false', '0']
    trues = ['true', '1']
    if string is None:
        return default
    elif string.lower() in trues:
        return True
    # elif string.lower() in falses:
    #     return False
    else:
        return False

@app.errorhandler(404)
def page_not_found(e):
    return '404<br>${}'.format(app.config['HIDDEN_URL'])

@app.route(app.config['HIDDEN_URL'] + '/help')
@login_required
def hidden_help():
    return render_template('hidden_help.html')

@app.route(app.config['HIDDEN_URL'])
@login_required
def hidden():
    # Handled within request
    tags = request.args.get('tags') or 'trap'
    try:
        page = int(request.args.get('page') or 1) - 1
    except (TypeError, ValueError):
        return '\"page\" parameter must be Integer.<br>Invalid \"page\" parameter: \"{}\"'.format(request.args.get('page'))
    # Handled within building
    try:
        count = int(request.args.get('count') or 50)
    except (TypeError, ValueError):
        return '\"count\" parameter must be Integer.<br>Invalid \"count\": \"{}\"'.format(request.args.get('count'))
    base64 = boolparse(request.args.get('base64'))
    # Handled within Jinja template
    print(request.args.get('showsample'))
    showsample = boolparse(request.args.get('showsample'), default=True)
    showtags = boolparse(request.args.get('showtags'))
    # Request, Parse & Build Data
    data = trap(tags, page, count, base64, showsample)
    print(showsample)
    return render_template('hidden.html', title='Gelbooru', data=data, base64=base64, showsample=showsample, showtags=showtags)

def base64ify(url):
    return base64.b64encode(requests.get(url).content).decode()

gelbooru_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags={}&pid={}&limit={}"

def trap(tags, page, count, base64, showsample):
    # URL Building & Request
    temp = gelbooru_url.format(tags, page, count)
    response = requests.get(temp).text
    # XML Parsing & Data Building
    parse = xmltodict.parse(response)
    build = []
    
    for index, element in enumerate(parse['posts']['post'][:count]):
        temp = {
                'index' : str(index + 1),
                'real_url' : element['@file_url'],
                'sample_url' : element['@preview_url'],
                'tags' : element['@tags']
                }
        if base64:
            if showsample:
                temp['base64'] = base64ify(temp['sample_url'])
            else:
                temp['base64'] = base64ify(temp['real_url'])

        build.append(temp)
    return build
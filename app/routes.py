from app import app, db, login
from app.models import User, Search
from app.forms import LoginForm, RegistrationForm
from app.custom import require_role
from werkzeug.urls import url_parse
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
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

@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('login'))

@app.route('/profile/')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/userinfo/')
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
    if current_user.is_authenticated:
        print(current_user)
    content = [{'text': fake.paragraph(nb_sentences=15),
                'seed': random.randint(0, 1000),
                'title': fake.word().title()}
               for _ in range(10)]
    return render_template('index.html', content=content)

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

# The only implementation I could get to work
def validate_id(id):
    id = str(id).strip()
    val = str(app.config['HIDDEN_URL']).strip()
    return id == val

def get_hidden():
    return "/hidden{}/".format(app.config['HIDDEN_URL'])

@app.route('/hidden<id>/history')
@login_required
@require_role(roles=['Hidden', 'Admin'])
def hidden_history(id):
    if not validate_id(id):
        return '<span style="color: red;">error:</span> bad id'
    return render_template('hidden_history.html')


@app.route('/hidden<id>/help')
@login_required
@require_role(roles=['Hidden'])
def hidden_help(id):
    if not validate_id(id):
        return '<span style="color: red;">error:</span> bad id'
    return render_template('hidden_help.html')

@app.route('/hidden<id>/')
@login_required
# @require_role(roles=['Hidden'])
def hidden(id):
    if not validate_id(id):
        return '<span style="color: red;">error:</span> bad id'
    # Handled within request
    tags = request.args.get('tags') or 'trap'
    try:
        page = int(request.args.get('page') or 1)
    except (TypeError, ValueError):
        return '\"page\" parameter must be Integer.<br>Invalid \"page\" parameter: \"{}\"'.format(request.args.get('page'))
    # Handled within building
    try:
        count = int(request.args.get('count') or 50)
    except (TypeError, ValueError):
        return '\"count\" parameter must be Integer.<br>Invalid \"count\": \"{}\"'.format(request.args.get('count'))
    base64 = boolparse(request.args.get('base64'))
    # Handled within Jinja template
    showfull = boolparse(request.args.get('showfull'))
    showtags = boolparse(request.args.get('showtags'))
    # Request, Parse & Build Data
    data = build_data(tags, page-1, count, base64, showfull)
    # Handling for limiters
    if base64:
        if showfull:
            count = min(25, count)
        else:
            count = min(50, count)
    # print(type(jsonify(request.args.to_dict())))
    search = Search(user_id=current_user.id, exact_url=str(request.url), query_args=json.dumps(request.args.to_dict()))
    db.session.add(search)
    db.session.commit()
    return render_template('hidden.html', title='Gelbooru Browser', data=data, tags=tags, page=page, count=count, base64=base64, showfull=showfull, showtags=showtags)

def base64ify(url):
    return base64.b64encode(requests.get(url).content).decode()

gelbooru_api_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags={}&pid={}&limit={}"
gelbooru_view_url = "https://gelbooru.com/index.php?page=post&s=view&id={}"

def build_data(tags, page, count, base64, showfull):
    # URL Building & Request
    temp = gelbooru_api_url.format(tags, page, count)
    response = requests.get(temp).text
    # XML Parsing & Data Building
    parse = xmltodict.parse(response)
    build = []
    
    try:
        parse['posts']['post']
    except KeyError:
        return build

    for index, element in enumerate(parse['posts']['post'][:count]):
        temp = {
                'index' : str(index + 1),
                'real_url' : element['@file_url'],
                'sample_url' : element['@preview_url'],
                # strips tags, ensures no empty tags (may be unnescary)
                'tags' : list(filter(lambda tag : tag != '', [tag.strip() for tag in element['@tags'].split(' ')])),
                'view' : gelbooru_view_url.format(element['@id'])
                }
        if base64:
            if not showfull:
                temp['base64'] = base64ify(temp['sample_url'])
            else:
                temp['base64'] = base64ify(temp['real_url'])

        build.append(temp)
    return build
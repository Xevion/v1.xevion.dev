from app import app, db, login
from app.models import User, Search
from app.forms import LoginForm, RegistrationForm
from app.custom import require_role
from werkzeug.urls import url_parse
from flask import render_template, redirect, url_for, flash, request, jsonify, abort, send_file, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from io import BytesIO
from textwrap import wrap
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Value
import mistune
import requests
import xmltodict
import base64
import random
import string
import faker
import json
import pprint
import os
import sys

print = pprint.PrettyPrinter().pprint
fake = faker.Faker()
markdown = mistune.Markdown()
strgen = lambda length, charset=string.ascii_letters, weights=None : ''.join(random.choices(list(charset), k=length, weights=weights))

@app.route('/ftbhot/about')
@app.route('/ftbhot/about/')
def ftbhot_about():
    return render_template('/ftbhot/about.html')

@app.route('/ftbhot/auth')
@app.route('/ftbhot/auth/')
def ftbhot_auth():
    return 'WIP'

@app.route('/ftbhot')
@app.route('/ftbhot/')
def ftbhot():
    return render_template('/ftbhot/embed.html')

@app.route('/ftbhot/json')
@app.route('/ftbhot/json/')
def ftbhot_embed():
    return render_template('/ftbhot/current.json')

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

@app.route('/keybase.txt')
def keybase():
    return app.send_static_file('keybase.txt')

@app.route('/modpacks')
def modpacks():
    return markdown(open(os.path.join(app.root_path, 'static', 'MODPACKS.MD'), 'r').read())

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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

@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('login'))

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=50)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/panzer/')
@app.route('/panzer')
@app.route('/panzer/<string>')
@app.route('/panzer/<string>/')
def panzer(string='bionicles are cooler than sex'):
    string = string.replace('+', ' ')
    string = string.replace('\n', '%0A')
    image = create_panzer(string)
    return serve_pil_image(image)

def create_panzer(string):
    img = Image.open("./app/static/panzer.jpeg")
    draw = ImageDraw.Draw(img)
    font1 = ImageFont.truetype('./app/static/arial.ttf', size=30)
    draw.text((10, 20), 'Oh panzer of the lake, what is your wisdom?', font=font1)
    font2 = ImageFont.truetype('./app/static/arial.ttf', size=30)
    topleft = (250, 500)
    wrapped = wrap(string, width=25)
    wrapped = [text.replace('%0A', '\n') for text in wrapped]
    for y, text in enumerate(wrapped):
        draw.text((topleft[0], topleft[1] + (y * 33)), text, font=font2)
    return img


@app.route('/profile/')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/api/')
def api():
    return 'fuckoff bots'

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
    # content = [{'text': fake.paragraph(nb_sentences=15),
    #             'seed': random.randint(0, 1000),
    #             'title': fake.word().title()}
    #            for _ in range(0)]
    content = [{'title': 'Work in Progress',
                'seed': random.randint(0, 1000),
                'text': 'This portion of my website is still a work in progress. I don\'t know if and when it\'ll be done, or how it will turn out in the end. - Xevion @ (Jul-11-2019)'}
               for _ in range(1)]
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
    val = str(app.config['HIDDEN_NUMBER']).strip()
    return id == val

def get_hidden():
    return "/hidden{}/".format(app.config['HIDDEN_NUMBER'])

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
@require_role(roles=['Hidden'])
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

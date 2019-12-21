from app import app, db, login
from app.models import User, Search
from app.forms import LoginForm, RegistrationForm
from app.custom import require_role
from werkzeug.urls import url_parse
from flask import render_template, redirect, url_for, flash, request, jsonify, abort, send_file
from flask_login import current_user, login_user, logout_user, login_required
from io import BytesIO
from textwrap import wrap
from PIL import Image, ImageDraw, ImageFont
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

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=50)
    img_io.seek(0)
    return flask.send_file(img_io, mimetype='image/jpeg')  

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
def default_profile():
    return profile(current_user.username)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

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

    # content = [{'text': fake.paragraph(nb_sentences=15),
    #             'seed': random.randint(0, 1000),
    #             'title': fake.word().title()}
    #            for _ in range(0)]
    content = [{'title': 'Work in Progress',
                'seed': random.randint(0, 1000),
                'text': 'This portion of my website is still a work in progress. I don\'t know if and when it\'ll be done, or how it will turn out in the end. - Xevion @ (Jul-11-2019)'}
               for _ in range(1)]
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
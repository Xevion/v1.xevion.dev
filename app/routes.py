from app import app
from app.models import User
from app.forms import LoginForm
from app.hidden import trap
from werkzeug.urls import url_parse
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
import random
import string
import faker
import json

fake = faker.Faker()

def strgen(length): return ''.join(
    random.choices(list(string.ascii_letters), k=length))

@app.route('/api')
def apoi():
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

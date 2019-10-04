from app import app
from flask import send_from_directory, redirect, url_for
import mistune
import os

markdown = mistune.Markdown()

@app.route('/keybase.txt')
def keybase():
    return app.send_static_file('keybase.txt')

@app.route('/modpacks')
def modpacks():
    return markdown(open(os.path.join(app.root_path, 'static', 'MODPACKS.MD'), 'r').read())

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('login'))
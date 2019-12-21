from app import app
from flask import send_from_directory, redirect, url_for, render_template
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

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404
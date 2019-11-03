from app import app
import json
import subprocess
import time
import os
from flask import send_from_directory, redirect, url_for, render_template, send_file


def check_and_update():
    path = os.path.join('app/spotify_explicit/recent.json')
    with open(path) as file:
        try:
            file = json.load(file)
        except json.JSONDecodeError:
            file = {'last_generated' : -1}
    regen = time.time() - 3600 >= file['last_generated']
    with open(path, 'w') as file:
        file = json.dump({'last_generated' : int(time.time())}, file)
    return regen
    
@app.route('/spotify/')
def spotify():
    if check_and_update():
        print('Graph out of date - running udpate command')
        r = subprocess.run(['python3', './app/spotify_explicit/main.py'])
    return send_file('spotify_explicit/export/export.png')
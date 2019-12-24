from app import app
from flask import send_file, redirect, url_for, render_template
from multiprocessing import Value
from mutagen.mp3 import MP3
import os
import re
import json
import subprocess

@app.route('/stream/<service>/<mediaid>')
def stream(service, mediaid):
    prepare(service, mediaid)
    config = service_functions[service].getConfig(mediaid)
    return send_file(os.path.join(os.path.dirname(__file__), '..', config['path']), attachment_filename=config['filename'])
    
# Prepares a URL for download, returning the duration it should play for if streamed
@app.route('/prepare/<service>/<mediaid>')
def prepare(service, mediaid):
    filepath = service_functions[service].path(mediaid)
    service_functions[service].download(mediaid)
    return str(MP3(filepath).info.length)
from app import app
from flask import send_file, redirect, url_for, render_template
from multiprocessing import Value
from mutagen.mp3 import MP3
import os
import re
import json
import subprocess

    @staticmethod
    def path(videoid):
        try:
            config = YouTubeHandler.getConfig(videoid)
            return config['path']
        except KeyError:
            filename = YouTubeHandler.filename(videoid)
            path = os.path.join('app', 'sounds', 'youtube', filename)
            with open(os.path.join('app', 'sounds', 'filenames.json'), 'r+') as file:
                config = json.load(file)
                config['youtube'][videoid] = {
                    "filename" : filename,
                    "path" : path
                }
                file.seek(0)
                file.write(json.dumps(config))
                file.truncate()
            return path
            
    @staticmethod
    def download(videoid):
        config = YouTubeHandler.getConfig(videoid)
        if not os.path.exists(config['path']):
            subprocess.run(['youtube-dl', '-x', '--restrict-filenames', '--audio-format', 'mp3', YouTubeHandler.url(videoid)])
            os.rename(config['filename'], config['path'])

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
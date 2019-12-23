from app import app
from flask import send_file, redirect, url_for, render_template
from mutagen.mp3 import MP3
import os
import re
import json
import subprocess

# Services => Expected Data
# YouTube => Video ID
# Soundcloud =>

# Filenaming/API Convention Examples
# Original URL/URI => API Path => Connected File
# https://www.youtube.com/watch?v=awtYiVGXiaY => /stream/youtube/awtYiVGXiaY => youtube/awtYiVGXiaY.mp3
# https://soundcloud.com/yungraredeath/fall-in-line-w-kxng-prod-mars-mission => /stream/soundcloud/fall-in-line-w-kxng-prod-mars-mission---yungraredeath => soundcloud/fall-in-line-w-kxng-prod-mars-mission---yungraredeath.mp3
# spotify:track:16PmczUxlX7dpr6ror6pXd => /duration/spotify/16PmczUxlX7dpr6ror6pXd => spotify/16PmczUxlX7dpr6ror6pXd.mp3

class YouTubeHandler:
    @staticmethod
    def url(videoid):
        return f'https://www.youtube.com/watch?v={videoid}'

    @staticmethod
    def getConfig(videoid):
        with open(os.path.join('app', 'sounds', 'filenames.json'), 'r') as file:
            return json.load(file)['youtube'][videoid]

    @staticmethod
    def filename(videoid):
        try:
            config = YouTubeHandler.getConfig(videoid)
            return config['filename']
        except KeyError:
            filename = subprocess.run(
                ['youtube-dl', '-x', '--audio-format', 'mp3', '--restrict-filenames', '--get-filename',
                YouTubeHandler.url(videoid)], encoding='utf-8', capture_output=True).stdout
            filename = filename.split('.')
            filename[-1] = 'mp3'
            return '.'.join(filename)

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
            print(os.listdir('.'))
            os.rename(config['filename'], config['path'])

service_functions = {
    'youtube' : YouTubeHandler,
    'spotify' : {'url' : None, 'path' : None},
    'soundcloud' : {'url' : None, 'path' : None}
}

if not os.path.exists(os.path.join('app', 'sounds', 'filenames.json')):
    with open(os.path.join('app', 'sounds', 'filenames.json'), 'r+') as file:
        json.dump({'youtube' : {} })    

# Streams a prepared MP3 back to the client
@app.route('/stream/<service>/<mediaid>')
def stream(service, mediaid):
    prepare(service, mediaid)
    if service == 'youtube':
        config = YouTubeHandler.getConfig(mediaid)
        return send_file(os.path.join(os.path.dirname(__file__), '..', config['path']), attachment_filename=config['filename'])
    return '???'
    
# Prepares a URL for download, returning the duration it should play for if streamed
@app.route('/prepare/<service>/<mediaid>')
def prepare(service, mediaid):
    filepath = service_functions[service].path(mediaid)
    service_functions[service].download(mediaid)
    print(filepath)
    return str(MP3(filepath).info.length)
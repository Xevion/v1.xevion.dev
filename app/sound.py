from app import app
from flask import send_file, redirect, url_for, render_template
from multiprocessing import Value
from mutagen.mp3 import MP3
import os
import re
import json
import subprocess
import shutil

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
            # Use stdout=PIPE, [Python 3.6] production server support instead of 'capture_output=True' => 'process.stdout'
            process = subprocess.Popen(
                ['youtube-dl', '-x', '--audio-format', 'mp3', '--restrict-filenames', '--get-filename', YouTubeHandler.url(videoid)],
                encoding='utf-8', stdout=subprocess.PIPE)
            filename = process.communicate()[0].split('.')
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
            os.rename(config['filename'], config['path'])

service_functions = {
    'youtube' : YouTubeHandler,
    'spotify' : SpotifyHandler,
    'soundcloud' : SoundcloudHandler
}

# Default JSON format, will be used in case of corruption
JSONDefault = {'youtube' : {}, 'soundcloud' : {}, 'spotify' : {}}

if not os.path.exists(os.path.join('app', 'sounds')):
    print('Sounds folder not found. Creating.')
    os.mkdir(os.path.join('app', 'sounds'))

# Test JSON file existence
if not os.path.exists(os.path.join('app', 'sounds', 'filenames.json')):
    print('JSON database file not found. Creating with default data structure.')
    with open(os.path.join('app', 'sounds', 'filenames.json'), 'w+') as file:
        json.dump({'youtube' : {} }, file)
else:
    # File exists, but is it valid JSON?
    try:
        print('Testing JSON database file.')
        with open(os.path.join('app', 'sounds', 'filenames.json'), 'r') as file:
            json.load(file)
    except json.JSONDecodeError:
        # Corruption or other has occurred. Clearing all service folders. Resetting and clearing all services
        print('Corruption/Invalid formatting in JSON file detected, clearing all config/media.')
        print('Clearing JSON database file.')
        with open(os.path.join('app', 'sounds', 'filenames.json'), 'w+') as file:
            json.dump(JSONDefault, file)

        for service in service_functions.keys():
            print(f"Clearing '{service}' folder.")
            servicePath = os.path.join('app', 'sounds', service)
            if os.path.exists(servicePath):
                shutil.rmtree(servicePath)
                os.mkdir(servicePath)
            else:
                os.mkdir(servicePath)

# Streams a prepared MP3 back to the client
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
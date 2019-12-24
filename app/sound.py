from app import app
from app.sound_models import YouTubeAudio, SoundcloudAudio
from flask import Response, send_file, redirect, url_for, render_template
from multiprocessing import Value
from mutagen.mp3 import MP3
import os
import re
import json
import subprocess

# Retrieves the YouTubeAudio object relevant to the mediaid if available. If not, it facilitiates the creation and writing of one.
# Also helps with access times.
def get_youtube(mediaid):
    audio = YouTubeAudio.query.filter_by(id=mediaid).first()
    if audio is not None:
        return audio.access()

# Returns the duration of a specificed media
@app.route('/stream/<service>/<mediaid>')
def stream(service, mediaid):
    if service == 'youtube':
        audio = get_youtube(mediaid)
        return send_file(audio.getPath(), attachment_filename=audio.filename)
    elif service == 'soundcloud':
        return Response('Not implemented', status=501, mimetype='application/json')
    elif service == 'spotify':
        return Response('Not implemented', status=501, mimetype='application/json')
    else:
        return Response('Bad request', status=400, mimetype='application/json')

# Returns the duration of a specific media
@app.route('/duration/<service>/<mediaid>')
def duration(service, mediaid):
    if service == 'youtube':
        duration = get_youtube(mediaid).durationn
        return Response(duration, status=200, mimetype='application/json')
    elif service == 'soundcloud':
        return Response('Not implemented', status=501, mimetype='application/json')
    elif service == 'spotify':
        return Response('Not implemented', status=501, mimetype='application/json')
    else:
        return Response('Bad request', status=400, mimetype='application/json')
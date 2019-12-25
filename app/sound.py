from app import app, db
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
        return audio # sets the access time to now
    audio = YouTubeAudio(id=mediaid)
    audio.fill_metadata()
    audio.download()
    # Commit and save new audio object into the database
    db.session.add(audio)
    db.session.commit()
    return audio

# Returns the duration of a specificed media
@app.route('/stream/<service>/<mediaid>')
def stream(service, mediaid):
    if service == 'youtube':
        audio = get_youtube(mediaid)
        return send_file(audio.getPath(alt=True), attachment_filename=audio.filename)
    elif service == 'soundcloud':
        return Response('Not implemented', status=501, mimetype='text/plain')
    elif service == 'spotify':
        return Response('Not implemented', status=501, mimetype='text/plain')
    else:
        return Response('Bad request', status=400, mimetype='text/plain')

# Returns the duration of a specific media
@app.route('/duration/<service>/<mediaid>')
def duration(service, mediaid):
    if service == 'youtube':
        duration = get_youtube(mediaid).duration
        return Response(str(duration), status=200, mimetype='text/plain')
    elif service == 'soundcloud':
        return Response('Not implemented', status=501, mimetype='text/plain')
    elif service == 'spotify':
        return Response('Not implemented', status=501, mimetype='text/plain')
    else:
        return Response('Bad request', status=400, mimetype='text/plain')

# Returns the duration of a specific media
@app.route('/status/<service>/<mediaid>')
def status(service, mediaid):
    if service == 'youtube':
        audio = get_youtube(mediaid).duration
        return Response(str(duration), status=200, mimetype='text/plain')
    elif service == 'soundcloud':
        return Response('Not implemented', status=501, mimetype='text/plain')
    elif service == 'spotify':
        return Response('Not implemented', status=501, mimetype='text/plain')
    else:
        return Response('Bad request', status=400, mimetype='text/plain')
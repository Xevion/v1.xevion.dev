from app import app, db, limiter
from app.sound_models import YouTubeAudio, SoundcloudAudio
from flask import Response, send_file, redirect, url_for, render_template, request
from multiprocessing import Value
from mutagen.mp3 import MP3
import os
import re
import json
import subprocess

# Selection of Lambdas for creating new responses
# Not sure if Responses change based on Request Context, but it doesn't hurt.
getBadRequest = lambda : Response('Bad request', status=400, mimetype='text/plain')
getNotImplemented = lambda : Response('Not implemented', status=501, mimetype='text/plain')
getInvalidID = lambda : Response('Invalid ID', status=400, mimetype='text/plain')
getNotDownloaded = lambda : Response('Media not yet downloaded', status=400, mimetype='text/plain')

# Retrieves the YouTubeAudio object relevant to the mediaid if available. If not, it facilitates the creation and writing of one.
# Also helps with access times.
def get_youtube(mediaid):
    audio = YouTubeAudio.query.get(mediaid)
    if audio is not None:
        audio.access()
        return audio # sets the access time to now
    else:
            audio = YouTubeAudio(id=mediaid)
            audio.fill_metadata()
            audio.download()
            # Commit and save new audio object into the database
            db.session.add(audio)
            db.session.commit()
            return audio

# Under the request context, it grabs the same args needed to decide whether the stream has been downloaded previously
# It applies rate limiting differently based on service, and whether the stream has been accessed previously
def downloadLimiter():
    service, mediaid = request.view_args['service'], request.view_args['mediaid']
    if service == 'youtube':
        if YouTubeAudio.query.get(mediaid) is not None:
            return '5/minute'
        else:
            return '1/30seconds'
    else:
        return '10/minute'

# Streams back the specified media back to the client
@app.route('/stream/<service>/<mediaid>')
@limiter.limit(downloadLimiter, error_message='Rate Limit Hit')
def stream(service, mediaid):
    if service == 'youtube':
        if YouTubeAudio.isValid(mediaid):
            audio = get_youtube(mediaid)
            return send_file(audio.getPath(alt=True), attachment_filename=audio.filename)
        else:
            return getInvalidID()
    elif service == 'soundcloud':
        return getNotImplemented()
    elif service == 'spotify':
        return getNotImplemented()
    else:
        return getBadRequest()

# Returns the duration of a specific media
@app.route('/duration/<service>/<mediaid>')
def duration(service, mediaid):
    if service == 'youtube':
        duration = get_youtube(mediaid).duration
        return Response(str(duration), status=200, mimetype='text/plain')
    elif service == 'soundcloud':
        return getNotImplemented()
    elif service == 'spotify':
        return getNotImplemented()
    else:
        return getBadRequest()

# Returns a detailed JSON export of a specific database entry.
# Will not create a new database entry where one didn't exist before.
@app.route('/status/<service>/<mediaid>')
def status(service, mediaid):
    if service == 'youtube':
        audio = YouTubeAudio.query.get(mediaid)
        if audio is None:
            if YouTubeAudio.isValid(mediaid):
                return getNotDownloaded()
            else:
                return getInvalidID()
        else:
            return Response(audio.toJSON(), status=200, mimetype='application/json')
    elif service == 'soundcloud':
        return getNotImplemented()
    elif service == 'spotify':
        return getNotImplemented()
    else:
        return getBadRequest()
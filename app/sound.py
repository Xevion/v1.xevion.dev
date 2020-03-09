from flask import Response, send_file, request, jsonify
from flask_login import current_user

from app import app, db, limiter
from app.sound_models import (
    YouTubeAudio,
    CouldNotDecode,
    CouldNotDownload,
    CouldNotProcess,
)

# Selection of Lambdas for creating new responses
# Not sure if Responses change based on Request Context, but it doesn't hurt.
getBadRequest = lambda: Response("Bad request", status=400, mimetype="text/plain")
getNotImplemented = lambda: Response(
    "Not implemented", status=501, mimetype="text/plain"
)
getInvalidID = lambda: Response("Invalid ID", status=400, mimetype="text/plain")
getNotDownloaded = lambda: Response(
    "Media not yet downloaded", status=400, mimetype="text/plain"
)


# Retrieves the YouTubeAudio object relevant to the mediaid if available. If not, it facilitates the creation and
# writing of one. Also helps with access times.
def get_youtube(mediaid):
    audio = YouTubeAudio.query.get(mediaid)
    if audio is not None:
        audio.access()
        return audio  # sets the access time to now
    else:
        audio = YouTubeAudio(id=mediaid)
        audio.fill_metadata()
        audio.download()
        # Commit and save new audio object into the database
        db.session.add(audio)
        db.session.commit()
        return audio


basic_responses = {
    CouldNotDecode: "Could not decode process response.",
    CouldNotDownload: "Could not download video.",
    CouldNotProcess: "Could not process.",
}


# A simple function among the routes to determine what should be returned. Not particularly sure how request context
# is passed, but it seems that either it passed or can access current_user's authentication/role's properly,
# so no problem. Shows error in full context IF authenticated + admin, otherwise basic error description, OTHERWISE a
# basic error message.
def errorCheck(e):
    if type(e) in basic_responses.keys():
        response = f"{basic_responses[type(e)]}"
    else:
        raise e
    if current_user.is_authenticated and current_user.has_role("Admin"):
        response = str(e) + "\n" + response
    return Response(response, status=200, mimetype="text/plain")


# Under the request context, it grabs the same args needed to decide whether the stream has been downloaded previously
# It applies rate limiting differently based on service, and whether the stream has been accessed previously
def downloadLimiter():
    if request.view_args["service"] == "youtube":
        if YouTubeAudio.query.get(request.view_args["mediaid"]) is not None:
            return "5/minute"
        else:
            return "1/30seconds"
    else:
        return "10/minute"


# Streams back the specified media back to the client
@app.route("/stream/<service>/<mediaid>")
@limiter.limit(downloadLimiter, lambda: "global", error_message="429 Too Many Requests")
def stream(service, mediaid):
    if service == "youtube":
        if YouTubeAudio.isValid(mediaid):
            try:
                audio = get_youtube(mediaid)
            except Exception as e:
                return errorCheck(e)
            return send_file(
                audio.getPath(alt=True), attachment_filename=audio.filename
            )
        else:
            return getInvalidID()
    elif service == "soundcloud":
        return getNotImplemented()
    elif service == "spotify":
        return getNotImplemented()
    else:
        return getBadRequest()


# Returns the duration of a specific media
@app.route("/duration/<service>/<mediaid>")
def duration(service, mediaid):
    if service == "youtube":
        duration = get_youtube(mediaid).duration
        return Response(str(duration), status=200, mimetype="text/plain")
    elif service == "soundcloud":
        return getNotImplemented()
    elif service == "spotify":
        return getNotImplemented()
    else:
        return getBadRequest()


# Returns a detailed JSON export of a specific database entry.
# Will not create a new database entry where one didn't exist before.
@app.route("/status/<service>/<mediaid>")
def status(service, mediaid):
    if service == "youtube":
        audio = YouTubeAudio.query.get(mediaid)
        if audio is None:
            if YouTubeAudio.isValid(mediaid):
                return getNotDownloaded()
            else:
                return getInvalidID()
        else:
            return Response(audio.toJSON(), status=200, mimetype="application/json")
    elif service == "soundcloud":
        return getNotImplemented()
    elif service == "spotify":
        return getNotImplemented()
    else:
        return getBadRequest()


@app.route("/list/<service>")
def list(service):
    if service == "youtube":
        audios = YouTubeAudio.query.all()
        return Response(
            ",".join(audio.id for audio in audios), status=200, mimetype="text/plain"
        )
    elif service == "soundcloud":
        return getNotImplemented()
    elif service == "spotify":
        return getNotImplemented()
    else:
        return getBadRequest()


@app.route("/all/<service>")
def all(service):
    if service == "youtube":
        audios = YouTubeAudio.query.all()
        return Response(
            jsonify([audio.toJSON(True) for audio in audios]),
            status=200,
            mimetype="application/json",
        )
    elif service == "soundcloud":
        return getNotImplemented()
    elif service == "spotify":
        return getNotImplemented()
    else:
        return getBadRequest()

import flask

from app import app


@app.route("/ftbhot/about")
@app.route("/ftbhot/about/")
def ftbhot_about():
    return flask.render_template("/ftbhot/about.html")


@app.route("/ftbhot/auth")
@app.route("/ftbhot/auth/")
def ftbhot_auth():
    return "WIP"


@app.route("/ftbhot")
@app.route("/ftbhot/")
def ftbhot():
    return flask.render_template("/ftbhot/embed.html")


@app.route("/ftbhot/json")
@app.route("/ftbhot/json/")
def ftbhot_embed():
    return flask.render_template("/ftbhot/current.json")

import base64
import json

import requests
import xmltodict
from flask import request, render_template
from flask_login import current_user, login_required

from app import app, db
from app.custom import require_role
from app.models import Search


@app.route("/hidden/history")
@login_required
@require_role(roles=["Hidden", "Admin"])
def hidden_history():
    return render_template("hidden_history.html")


@app.route("/hidden/help")
@login_required
@require_role(roles=["Hidden"])
def hidden_help():
    return render_template("hidden_help.html")


# Parses strings to test for "boolean qualities"
def boolparse(string, default=False):
    trues = ["true", "1"]
    if string is None:
        return default
    elif string.lower() in trues:
        return True
    return False


@app.route("/hidden/")
@login_required
@require_role(roles=["Hidden"])
def hidden():
    # Handled within request
    tags = request.args.get("tags") or "trap"
    try:
        page = int(request.args.get("page") or 1)
    except (TypeError, ValueError):
        return '"page" parameter must be Integer.<br>Invalid "page" parameter: "{}"'.format(
            request.args.get("page")
        )
    # Handled within building
    try:
        count = int(request.args.get("count") or 50)
    except (TypeError, ValueError):
        return '"count" parameter must be Integer.<br>Invalid "count": "{}"'.format(
            request.args.get("count")
        )
    base64 = boolparse(request.args.get("base64"))
    # Handled within Jinja template
    showfull = boolparse(request.args.get("showfull"))
    showtags = boolparse(request.args.get("showtags"))
    # Request, Parse & Build Data
    data = build_data(tags, page - 1, count, base64, showfull)
    # Handling for limiters
    if base64:
        if showfull:
            count = min(25, count)
        else:
            count = min(50, count)
    search = Search(
        user_id=current_user.id,
        exact_url=str(request.url),
        query_args=json.dumps(request.args.to_dict()),
    )
    db.session.add(search)
    db.session.commit()
    return render_template(
        "hidden.html",
        title="Gelbooru Browser",
        data=data,
        tags=tags,
        page=page,
        count=count,
        base64=base64,
        showfull=showfull,
        showtags=showtags,
    )


def base64ify(url):
    return base64.b64encode(requests.get(url).content).decode()


gelbooru_api_url = (
    "https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags={}&pid={}&limit={}"
)
gelbooru_view_url = "https://gelbooru.com/index.php?page=post&s=view&id={}"


def build_data(tags, page, count, base64, showfull):
    # URL Building & Request
    temp = gelbooru_api_url.format(tags, page, count)
    response = requests.get(temp).text
    # XML Parsing & Data Building
    parse = xmltodict.parse(response)
    build = []

    try:
        parse["posts"]["post"]
    except KeyError:
        return build

    for index, element in enumerate(parse["posts"]["post"][:count]):
        temp = {
            "index": str(index + 1),
            "real_url": element["@file_url"],
            "sample_url": element["@preview_url"],
            # strips tags, ensures no empty tags (may be unnecessary)
            "tags": list(
                filter(
                    lambda tag: tag != "",
                    [tag.strip() for tag in element["@tags"].split(" ")],
                )
            ),
            "view": gelbooru_view_url.format(element["@id"]),
        }
        if base64:
            if not showfull:
                temp["base64"] = base64ify(temp["sample_url"])
            else:
                temp["base64"] = base64ify(temp["real_url"])

        build.append(temp)
    return build

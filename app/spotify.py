import json
import os
import time

from flask import send_file

from app import app
from config import Config
from .spotify_explicit import main

path = os.path.join("app/spotify_explicit/recent.json")


def check_and_update():
    try:
        with open(path) as file:
            file = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        file = {"last_generated": -1}

    if file["last_generated"] == -1:
        return True
    else:
        dif = time.time() - file["last_generated"]
        # print('dif', dif)
        if dif >= Config.SPOTIFY_CACHE_TIME:
            return True
        else:
            ideal = file["last_generated"] + Config.SPOTIFY_CACHE_TIME
            # print(f'Waiting another {int(ideal - time.time())} seconds')
    return False


@app.route("/spotify/")
def spotify():
    if check_and_update():
        print("Graph out of date - running update command")
        with open(path, "w+") as file:
            file = json.dump({"last_generated": int(time.time())}, file)
        main.main()
    return send_file("spotify_explicit/export/export.png")

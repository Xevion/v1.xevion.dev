import json
import logging
import os
import sys
import time

from . import auth
from . import process
from . import pull


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Pulling data from Spotify")
    refresh()
    process.main()


# Refreshes tracks from files if the token from Spotipy has expired,
# thus keeping us up to date in most cases while keeping rate limits
def refresh():
    file_path = os.path.join(sys.path[0], f".cache-{auth.USERNAME}")
    if os.path.exists(file_path):
        cache = json.load(open(file_path, "r"))
        if True or time.time() > cache["expires_at"]:
            logging.info(
                "Refreshing Spotify data by pulling tracks, this may take a moment."
            )
            pull.main()
        else:
            logging.info(
                "Spotify data deemed to be recent enough (under {} seconds old)".format(
                    cache["expires_in"]
                )
            )
    else:
        pull.main()


if __name__ == "__main__":
    main()

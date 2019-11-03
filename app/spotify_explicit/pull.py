import os
import sys
import auth
import json
import shutil
import pprint
import spotipy
import logging
from hurry.filesize import size, alternative
import spotipy.util as util

def main():
    # Get Authorization
    logging.basicConfig(level=logging.INFO)
    logging.info('Authorizing with Spotify via Spotipy')
    logging.warning('May require User Interaction to authenticate properly!')
    token = util.prompt_for_user_token(
        username=auth.USERNAME,
        scope=auth.SCOPE,
        client_id=auth.CLIENT_ID,
        client_secret=auth.CLIENT_SECRET,
        redirect_uri=auth.REDIRECT_URI
    )
    sp = spotipy.Spotify(auth=token)
    logging.info('Authorized with Spotify via Spotipy')

    tracks_folder = os.path.join(sys.path[0], 'tracks')
    logging.warning('Clearing all files in tracks folder for new files')
    if os.path.exists(tracks_folder):
        shutil.rmtree(tracks_folder) # Delete folder and all contents (old track files)
    os.makedirs(tracks_folder) # Recreate the folder just deleted
    logging.info('Cleared folder, ready to download new track files')

    curoffset, curlimit = 0, 50
    while curoffset >= 0:
        # Request and identify what was received
        logging.info('Requesting {} to {}'.format(curoffset, curoffset + curlimit))
        response = sp.current_user_saved_tracks(limit=curlimit, offset=curoffset)
        received = len(response['items'])
        logging.info('Received {} to {}'.format(curoffset, curoffset + received))
        # Create path/filename
        filename = f'saved-tracks-{curoffset}-{curoffset + received}.json'
        filepath = os.path.join(tracks_folder, filename)
        # Save track file
        with open(filepath, 'w+') as file:
            json.dump(response, file)
        logging.info('Saved at "{}" ({})'.format(
            f'\\tracks\\{filename}',
            size(os.path.getsize(filepath)))
        )
        # Decide whether we have received all possible tracks
        if received < curlimit:
            logging.info('Requested and saved {} tracks split over {} files ({})'.format(
                curoffset + received,
                len(os.listdir(tracks_folder)),
                size(
                    sum(
                        os.path.getsize(os.path.join(tracks_folder, file)) for file in os.listdir(tracks_folder)
                    ),
                    system=alternative
                )
            ))
            break
        # Continuing, so increment offset
        curoffset += curlimit
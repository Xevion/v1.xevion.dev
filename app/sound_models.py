import json
import os
import re
import subprocess
from datetime import datetime

from app import db


# Returned when a erroring status code is returned. May end up hitting false positives, where the file was still produced properly
# yet a erroring status code was returned. May be a good measure to always disconnect when a error code is found.
# Takes precedence over CouldNotDownload and CouldNotDecode exceptions.
class CouldNotProcess(Exception):
    pass


# Shouldn't happen in most cases. When a file isn't found, yet the status code for the process returned positive.
class CouldNotDownload(Exception):
    pass


# When a JSON returning command returns undecodable JSON
# This shouldn't occur and will only be available when a unforseen error occurs where JSON cannot be read,
# yet a non-erroring status code was returned!
class CouldNotDecode(Exception):
    pass


# A Database Object describing a Audio File originating from YouTube
# Stores basic information like Title/Uploader/URL etc. as well as holds methods useful
# for manipulating, deleting, downloading, updating, and accessing the relevant information or file.
class YouTubeAudio(db.Model):
    id = db.Column(db.String(11),
                   primary_key=True)  # 11 char id, presumed to stay the same for the long haul. Should be able to change to 12 chars.
    url = db.Column(db.String(64))  # 43 -> 64
    title = db.Column(db.String(128))  # 120 > 128
    creator = db.Column(db.String(128))  # Seems to be Uploader set, so be careful with this
    uploader = db.Column(db.String(32))  # 20 -> 32
    filename = db.Column(db.String(156))  # 128 + 11 + 1 -> 156
    duration = db.Column(db.Integer)
    access_count = db.Column(db.Integer, default=0)
    download_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_access_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Marks a database entry as accessed by updating timestamps and counts
    def access(self):
        print(f'{self.id} was just accessed ')
        self.access_count = (self.access_count or 0) + 1
        self.last_access_timestamp = datetime.utcnow()
        db.session.commit()
        return self

    # Returns the path for the database entry's audio file
    # alt: sendfile() asks for a path originating from ./app/
    def getPath(self, alt=False):
        if alt:
            return os.path.join('sounds', 'youtube', self.filename)
        return os.path.join('app', 'sounds', 'youtube', self.filename)

    def file_exists(self):
        return os.path.exists(self.getPath())

    # Fills in all metadata for a database entry
    def fill_metadata(self):
        print(f'Filling out metadata for {self.id}')
        # Use stdout=PIPE, [Python 3.6] production server support instead of 'capture_output=True' => 'process.stdout'
        self.filename = self.id + '.mp3'
        command = f'youtube-dl -4 -x --audio-format mp3 --restrict-filenames --dump-json {self.id}'
        process = subprocess.Popen(command.split(' '),
                                   encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = process.communicate()
        if process.returncode != 0:
            raise CouldNotProcess(
                f'Command: {command}\n{data[1]}Exit Code: {process.returncode}')  # process ends with a newline, not needed between
        try:
            data = json.loads(data[0])
        except json.JSONDecodeError:
            raise CouldNotDecode(
                data)  # We'll return the process data, figure out what to do with it higher up in stack (return/diagnose etc.)
        print(f'JSON acquired for {self.id}, beginning to fill.')
        self.duration = data['duration']
        self.url = data['webpage_url']  # Could be created, but we'll just infer from JSON response
        self.creator = data['creator'] or data['uploader']
        self.uploader = data['uploader'] or data['creator']
        self.title = data['title'] or data[
            'alt_title']  # Do not trust alt-title ; it is volatile and uploader set, e.x. https://i.imgur.com/Tgff4rI.png
        print(f'Metadata filled for {self.id}')
        db.session.commit()

    # Begins the download process for a video
    def download(self):
        print(f'Attempting download of {self.id}')
        command = f'youtube-dl -x -4 --restrict-filenames --audio-quality 64K --audio-format mp3 -o ./app/sounds/youtube/%(id)s.%(ext)s {self.id}'
        process = subprocess.Popen(command.split(' '), encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = process.communicate()  # Not the data for the mp3, just the output. We have to separate this in order to 'wait' for the process to complete fully.
        print('Checking process return code...')
        if process.returncode != 0:
            raise CouldNotProcess(f'Command: {command}\n{data[1] or data[0]}Exit Code: {process.returncode}')
        print('Checking for expected file...')
        if not os.path.exists(self.getPath()):
            raise CouldNotDownload(data[1] or data[0])
        print(f'Download attempt for {self.id} finished successfully.')

        # Validates whether the specified ID could be a valid YouTube video ID

    @staticmethod
    def isValid(id):
        return re.match(r'^[A-Za-z0-9_-]{11}$', id) is not None

    # Returns a JSON serialization of the database entry
    def toJSON(self, noConvert=False):
        data = {'id': self.id, 'url': self.url, 'title': self.title, 'creator': self.creator,
                'uploader': self.uploader, 'filename': self.filename, 'duration': self.duration,
                'access_count': self.access_count, 'download_timestamp': self.download_timestamp.isoformat(),
                'last_access_timestamp': self.last_access_timestamp.isoformat()}
        return data if noConvert else json.dumps(data)

    def delete(self):
        path = os.path.join('app', 'sounds', 'youtube', self.filename)
        try:
            os.remove(path)
        except:
            print(f'[{self.id}] Could not delete relevant file "{path}".')
        db.session.delete(self)
        db.session.commit()


class SoundcloudAudio(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # hidden API-accessible only ID
    url = db.Column(db.String(256))
    title = db.Column(db.String(128))
    creator = db.Column(db.String(64))
    filename = db.Column(db.String(156))
    duration = db.Column(db.Integer)

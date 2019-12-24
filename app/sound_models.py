from datetime import datetime
from app import db
import subprocess
import json
import os

class YouTubeAudio(db.Model):
    id = db.Column(db.String(11), primary_key=True) # 11 char id, presumed to stay the same for the long haul. Should be able to change to 12 chars.
    url = db.Column(db.String(64)) # 43 -> 64
    title = db.Column(db.String(128)) # 120 > 128
    creator = db.Column(db.String(128)) # Seems to be Uploader set, so be careful with this
    uploader = db.Column(db.String(32)) # 20 -> 32
    filename = db.Column(db.String(156)) # 128 + 11 + 1 -> 156 
    duration = db.Column(db.Integer) 
    access_count = db.Column(db.Integer)
    download_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_access_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def access(self):
        self.access_count += 1
        self.last_access_timestamp = datetime.utcnow()
        db.session.commit()
        return self

    def getPath(self):
        return os.path.join('app', 'sounds', 'youtube', self.filename)

    def file_exists(self):
        return os.path.exists(self.getPath())

    def fill_metadata(self):
        # Use stdout=PIPE, [Python 3.6] production server support instead of 'capture_output=True' => 'process.stdout'
        self.url = f'https://www.youtube.com/watch?v={self.id}'
        processFilename = subprocess.Popen(['youtube-dl', '-x', '--audio-format', 'mp3', '--restrict-filenames', '--get-filename', self.url],
                encoding='utf-8', stdout=subprocess.PIPE)
        self.filename = processFilename.communicate()[0].split('.')[0] + 'mp3'
        processJSON = subprocess.Popen(['youtube-dl', '-x', '--audio-format', 'mp3', '--restrict-filenames', '--dump-json', self.url],
                encoding='utf-8', stdout=subprocess.PIPE)
        data = json.loads(processJSON.communicate()[0])
        self.duration = data['duration']
        self.creator = data['creator'] or data['uploader']
        self.uploader = data['uploader'] or data['creator']
        self.title = data['title'] or data['alt_title'] # Do not trust alt-title ; it is volatile and uploader set, e.x. https://i.imgur.com/Tgff4rI.png

    def download(self):
        subprocess.run(['youtube-dl', '-x', '--restrict-filenames', '--audio-format', 'mp3', self.id])
        os.rename(self.filename, self.getPath())

class SoundcloudAudio(db.Model):
    id = db.Column(db.Integer, primary_key=True) # hidden API-accessible only ID
    url = db.Column(db.String(256))
    title = db.Column(db.String(128))
    creator = db.Column(db.String(64))
    filename = db.Column(db.String(156))
    duration = db.Column(db.Integer)
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
    access_count = db.Column(db.Integer, default=0)
    download_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_access_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def access(self):
        print(f'{self.id} was just accessed ')
        self.access_count = (self.access_count or 0) + 1
        self.last_access_timestamp = datetime.utcnow()
        db.session.commit()
        return self

    def getPath(self, alt=False):
        if alt:
            return os.path.join('sounds', 'youtube', self.filename)
        return os.path.join('app', 'sounds', 'youtube', self.filename)

    def file_exists(self):
        return os.path.exists(self.getPath())

    def fill_metadata(self):
        print(f'Filling out metadata for {self.id}')
        # Use stdout=PIPE, [Python 3.6] production server support instead of 'capture_output=True' => 'process.stdout'
        self.filename = self.id + '.mp3'
        print(f'Filename acquired for {self.id}')
        processJSON = subprocess.Popen(f'youtube-dl -4 -x --audio-format mp3 --restrict-filenames --dump-json {self.id}'.split(' '),
                encoding='utf-8', stdout=subprocess.PIPE)
        data = json.loads(processJSON.communicate()[0])
        print(f'JSON acquired for {self.id}, beginning to fill.')
        self.duration = data['duration']
        self.creator = data['creator'] or data['uploader']
        self.uploader = data['uploader'] or data['creator']
        self.title = data['title'] or data['alt_title'] # Do not trust alt-title ; it is volatile and uploader set, e.x. https://i.imgur.com/Tgff4rI.png
        print(f'Metadata filled for {self.id}')
        db.session.commit()

    def download(self):
        print(f'Downloading MP3 for {self.id}')
        subprocess.run(f'youtube-dl -x -4 --restrict-filenames --audio-format mp3 -o ./app/sounds/youtube/%(id)s.%(ext)s {self.id}'.split(' '))
        # os.rename(self.filename, self.getPath())
        print(f'Finished moving {self.id} into proper folder')

    def delete(self):
        os.remove(os.path.join('app', 'sounds', 'youtube', self.filename))
        db.session.delete(self)
        db.session.commit()

class SoundcloudAudio(db.Model):
    id = db.Column(db.Integer, primary_key=True) # hidden API-accessible only ID
    url = db.Column(db.String(256))
    title = db.Column(db.String(128))
    creator = db.Column(db.String(64))
    filename = db.Column(db.String(156))
    duration = db.Column(db.Integer)
from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from marshmallow import post_load, fields, ValidationError
from dotenv import load_dotenv
from os import environ

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    album = db.Column(db.String(255))
    release_date = db.Column(db.Date)
    genre = db.Column(db.String(255))
    likes = db.Column(db.Integer, default = 0)

#from a design standpoint, needed a way to default 'likes' to 0 upon creation so that the patch function to create a like works corerctly on newly created items
 

    def __repr__(self):
        return f'{self.id} {self.title} {self.artist} {self.album} {self.release_date} {self.genre} {self.likes}'

# Schemas

class SongSchema(ma.Schema):
    id = fields.Integer(primary_key=True)
    title = fields.String(required=True)
    artist = fields.String(required=True)
    album = fields.String()
    release_date = fields.Date()
    genre = fields.String()
    likes = fields.Integer()

    class Meta:
        fields = ("id", "title", "artist", "album", "release_date", "genre", "likes")

    @post_load
    def create_song(self, data, **kwargs):
        return Song(**data)

song_schema = SongSchema()
songs_schema = SongSchema(many=True)

# Resources

class SongListResource(Resource):
    def get(self):
        all_songs =  Song.query.all()
        return songs_schema.dump(all_songs)
    
    def post(self):
        form_data = request.get_json()
        try:        
            new_song = song_schema.load(form_data)
            db.session.add(new_song)
            db.session.commit()
            return song_schema.dump(new_song), 201
        except ValidationError as err:
            return err.messages, 400

class SongResource(Resource):
    def get(self, song_id):
        song_from_db = Song.query.get_or_404(song_id)
        return song_schema.dump(song_from_db)
    
    def put(self, song_id):
        song_from_db = Song.query.get_or_404(song_id)

        if 'title' in request.json:
            song_from_db.title = request.json['title']
        if 'artist' in request.json:
            song_from_db.artist = request.json['artist']       
        if 'album' in request.json:
            song_from_db.album = request.json['album']  
        if 'release_date' in request.json:
            song_from_db.release_date = request.json['release_date']   
        if 'genre' in request.json:
            song_from_db.genre = request.json['genre']   
        if 'likes' in request.json:
            return 'not_permitted_to_reset', 400

        db.session.commit()
        return song_schema.dump(song_from_db)

#Decided from a design standpoint decided to not let like be an editable field, 
# the only edit to that field would be to increase likes

    def patch(self, song_id):
        song_from_db = Song.query.get_or_404(song_id)
        song_from_db.likes += 1
        db.session.commit()
        return song_schema.dump(song_from_db)

    def delete(self, song_id):
        song_from_db = Song.query.get_or_404(song_id)
        db.session.delete(song_from_db)
        db.session.commit()
        return '', 204

# Routes
api.add_resource(SongListResource, '/api/songs')
api.add_resource(SongResource, '/api/songs/<int:song_id>')



class SongSchema(ma.Schema):
    id = fields.Integer(primary_key=True)
    title = fields.String(required=True)
    artist = fields.String(required=True)
    album = fields.String()
    release_date = fields.Date()
    genre = fields.String()

    class Meta:
        fields = ("id", "title", "artist", "album", "release_date", "genre")

    @post_load
    def create_song(self, data, **kwargs):
        return Song(**data)

song_schema = SongSchema()
songs_schema = SongSchema(many=True)


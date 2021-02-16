from server.database.db import db


class Driver(db.Document):
    name = db.StringField(required=True, unique=True)


class Car(db.Document):
    name = db.StringField(required=True, unique=True)
    type = db.StringField(required=True)


class Track(db.Document):
    name = db.StringField(required=True, unique=True)
    variant = db.StringField(required=True)


class LapTime(db.Document):
    driver = db.ReferenceField(Driver, required=True)
    car = db.ReferenceField(Car, required=True)
    track = db.ReferenceField(Track, required=True)
    session_type = db.StringField(required=True)
    time = db.FloatField(required=True)
    recorded_at = db.FloatField(required=True)

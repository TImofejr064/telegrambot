from peewee import *
import datetime

db = SqliteDatabase('bot.db')

class User(Model):
    userId = CharField()
    username = CharField()


    class Meta:
        database = db

class Status(Model):
    status = CharField()

    class Meta:
        database = db   

class Task(Model):
    headline = CharField(max_length=40)
    text = TextField()
    status = ForeignKeyField(Status)
    date = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(User)
    
    class Meta:
        database = db


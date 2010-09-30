from google.appengine.ext import db

class Photo(db.Model):
	dateCreated = db.DateTimeProperty()
	blobKey = db.StringProperty()
	description = db.StringProperty()
	title = db.StringProperty()

class Competition(db.Model):
	dateCreated = db.DateTimeProperty()
	photoKey = db.ReferenceProperty(Photo)
	complete = db.BooleanProperty()
	
class Caption(db.Model):
	text = db.StringProperty()
	dateCreated = db.DateTimeProperty()
	author = db.StringProperty()
	competitionKey = db.ReferenceProperty(Competition)
	approved = db.BooleanProperty(default=False)
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images

from models import Photo, Competition, Caption
from google.appengine.ext.webapp import template

from django.utils import simplejson

import os, logging, datetime, cgi

class AdminHandler(webapp.RequestHandler):
    def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), 'templates/admin.html')
		self.response.out.write(template.render(path, template_values))
		
class ColophonHandler(webapp.RequestHandler):
    def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), 'templates/colophon.html')
		self.response.out.write(template.render(path, template_values))

class CreateCompetitionHandler(webapp.RequestHandler):
	def get(self):
		template_values = {}
		template_values['upload_url'] = blobstore.create_upload_url('/photo/upload')
		path = os.path.join(os.path.dirname(__file__), 'templates/create-competition.html')
		self.response.out.write(template.render(path, template_values))

class LatestCompetitionHandler(webapp.RequestHandler):
	def get(self):
		template_values = {}
		competition = Competition.all().order("-dateCreated").get()
		photo = competition.photoKey # get photo instance
		photoId = photo.key().id()
		page = 0;
		competitionId = competition.key().id()
		showPagination = False
		captions = Caption.all().filter('competitionKey =',competition.key()).fetch(limit=11)
		if len(captions) == 11:
			showPagination = True
			captions.pop(10)
			page = page+1
		template_values['img'] = "/photo/%s" % photoId # get id from photo instance, to pass later in URL
		template_values['title'] = photo.title
		template_values['description'] = photo.description
		template_values['photoId'] = photoId
		template_values['competitionId'] = competitionId
		template_values['captions'] = captions
		template_values['complete'] = competition.complete
		template_values['pageNum'] = photo.title
		template_values['showPagination'] = showPagination
		template_values['page'] = page
		path = os.path.join(os.path.dirname(__file__), 'templates/competition.html')
		self.response.out.write(template.render(path, template_values))
		
class PhotoDownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, id):
		photo = Photo.get_by_id(int(id))
		blobKey = photo.blobKey
		
		if blobKey:
			blobinfo = blobstore.get(blobKey)
		
			if blobinfo:
				aspect = 'h'
				img = images.Image(blob_key=blobKey)
				img.rotate(180)
				thumbnail = img.execute_transforms(output_encoding=images.JPEG)
				if img.width > img.height:
					pass
				else:
					aspect = 'v'
				#img.im_feeling_lucky()
				img = images.Image(blob_key=blobKey)
				if aspect == 'h':
					img.resize(width=505)
				else:
					img.resize(width=355)
				thumbnail = img.execute_transforms(output_encoding=images.JPEG)
				self.response.headers['Content-Type'] = 'image/jpeg'
				self.response.out.write(thumbnail)
				return

		self.error(404)

class CompetitionsHandler(webapp.RequestHandler):
	def get(self):
		template_values = {}
		li = []
		competitions = Competition.all().order("-dateCreated").fetch(limit=10)
		for comp in competitions:
			photo = comp.photoKey # get photo instance
			li.append( { 'date' : comp.dateCreated, 'id' : comp.key().id(), 'complete' : comp.complete, 'title' : photo.title } )
		template_values['competitions'] = li
		path = os.path.join(os.path.dirname(__file__), 'templates/competitions.html')
		self.response.out.write(template.render(path, template_values))

class CaptionsHandler(webapp.RequestHandler):
	def get(self):
		template_values = {}
		captions = Caption.all().order("-dateCreated").fetch(limit=100)
		template_values['captions'] = captions
		path = os.path.join(os.path.dirname(__file__), 'templates/captions.html')
		self.response.out.write(template.render(path, template_values))
				
class CompetitionHandler(webapp.RequestHandler):
	def get(self, id, page=0, json=None):
		offset = 0
		p = 0
		if page:
			offset = 6*int(page)
			p = page
		template_values = {}
		competition = Competition.get_by_id(int(id))
		photo = competition.photoKey # get photo instance
		showPagination = False
		captions = Caption.all().filter('competitionKey =',competition).fetch(offset=offset, limit=11)
		if len(captions) == 11:
			showPagination = True
			p = p+1
			captions.pop(10)
		
		if json == 'json':
			jsonCaptions = []
			for c in captions:
				jc = { "text" : c.text,
						"author" : c.author
					}
				jsonCaptions.append(jc)	
			self.response.headers['Content-Type'] = "application/json"
			self.response.out.write(simplejson.dumps([jsonCaptions, showPagination]))
			return
		template_values['img'] = "/photo/%s" % photo.key().id() # get id from photo instance, to pass later in URL
		template_values['title'] = photo.title
		template_values['description'] = photo.description
		template_values['competitionId'] = id
		template_values['complete'] = competition.complete
		template_values['captions'] = captions
		template_values['showPagination'] = showPagination
		template_values['page'] = p
		path = os.path.join(os.path.dirname(__file__), 'templates/competition.html')
		self.response.out.write(template.render(path, template_values))
		
class CaptionSubmitHandler(webapp.RequestHandler):
	def post(self):
		try:
			template_values = {}
			competitionId = self.request.get('competitionId')
			competition = Competition.get_by_id(int(competitionId)).key()
			captionText = cgi.escape(self.request.get('caption'))
			authorText = self.request.get('author')
			caption = Caption(text=captionText, author=authorText, competitionKey=competition)
			caption.put()
			self.redirect("/success");
		except:
			self.redirect("/failure");
			
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		try:
			upload = self.get_uploads('file')
			blob = upload[0]
			description = self.request.get('description');
			title = self.request.get('title');
			photo = Photo(blobKey=str(blob.key()), description=description, title=title)
			photo.put()
			competition = Competition(photoKey=photo.key(), dateCreated=datetime.datetime.now())
			competition.put();
			self.redirect("/competitions/latest")
		except:
			self.redirect("/upload-failure")

class AdminCompetitionsHandler(webapp.RequestHandler):
    def get(self):
		template_values = {}
		li = []
		competitions = Competition.all().order('-dateCreated').fetch(limit=10)
		for comp in competitions:
			li.append( { 'date' : comp.dateCreated, 'id' : comp.key().id(), 'complete' : comp.complete } )
		template_values['competitions'] = li
		path = os.path.join(os.path.dirname(__file__), 'templates/admin_competitions.html')
		self.response.out.write(template.render(path, template_values))

class StartCompetitionHandler(webapp.RequestHandler):
	def get(self, id):
		template_values = {}
		competition = Competition.get_by_id(int(id))
		competition.complete = False
		competition.put()
		self.redirect('/admin/competitions')
		
class EndCompetitionHandler(webapp.RequestHandler):
	def get(self, id):
		template_values = {}
		competition = Competition.get_by_id(int(id))
		competition.complete = True
		competition.put()
		self.redirect('/admin/competitions')

class SuccessHandler(webapp.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), 'templates/success.html')
		self.response.out.write(template.render(path, template_values))
		
class ErrorHandler(webapp.RequestHandler):
    def get(self):
		self.response.out.write('Oops, error! This is more like a CRAPtion Competition, isn\'t it?')

def main():
    application = webapp.WSGIApplication([
											('/photo/([0-9]*)', PhotoDownloadHandler),
											
											('/competitions/all|/competitions', CompetitionsHandler),
											('^/$|/competitions/latest', LatestCompetitionHandler),
											('/competitions/([0-9]*)', CompetitionHandler),
											('/competitions/([0-9]*)/page/([0-9]*)', CompetitionHandler),
											('/competitions/([0-9]*)/page/([0-9]*)/(json)', CompetitionHandler),
											('/competitions/([0-9]*)/end', EndCompetitionHandler),
											('/admin/competitions/([0-9]*)/start', StartCompetitionHandler),
											
											('/admin', AdminHandler),
											('/admin/competition/create', CreateCompetitionHandler),
											('/admin/competitions', AdminCompetitionsHandler),
											
											('/photo/upload', UploadHandler),
											
											('/caption/submit', CaptionSubmitHandler),
											('/captions', CaptionsHandler),
											
											('/success', SuccessHandler),
											('/colophon', ColophonHandler),
											('/.*', ErrorHandler),
										],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

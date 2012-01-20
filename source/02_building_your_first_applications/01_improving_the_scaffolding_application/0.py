# -*- coding: utf-8 -*-

from gluon.storage import Storage
settings = Storage()

settings.production = False

if settings.production:
   settings.db_uri = 'sqlite://production.sqlite'
   settings.migrate = False
else:
   settings.db_uri = 'sqlite://development.sqlite'
   settings.migrate = True

settings.title = request.application
settings.subtitle = 'write something here'
settings.author = 'you'
settings.author_email = 'you@example.come'
settings.keywords = ''
settings.description = ''
settings.layout_theme = 'Default'
settings.security_key = 'a098c897-724b-4e05-b2d8-8ee993385ae6'
settings.email_server = 'localhost'
settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = '' 

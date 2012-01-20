# -*- coding: utf-8 -*-

from gluon.tools import *

db = DAL(settings.db_uri)
if settings.db_uri.startswith('gae'):
    session.connect(request, response, db = db)

mail = Mail()                                  # mailer
auth = Auth(db)                      # authentication/authorization
crud = Crud(db)                      # for CRUD helpers using auth
service = Service()                  # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

# enable generic views for all actions for testing purpose
response.generic_patterns = ['*']

mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login
auth.settings.hmac_key = settings.security_key

# add any extra fields you may want to add to auth_user
auth.settings.extra_fields['auth_user'] = []

# user username as well as email
auth.define_tables(migrate=settings.migrate,username=True)
auth.settings.mailer = mail
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user', args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user', args=['reset_password'])+'/%(key)s to reset your password'

if settings.login_method=='janrain':
   from gluon.contrib.login_methods.rpx_account import RPXAccount
   auth.settings.actions_disabled=['register', 'change_password', 'request_reset_password']
   auth.settings.login_form = RPXAccount(request,
       api_key = settings.login_config.split(':')[-1],
       domain = settings.login_config.split(':')[0],
       url = "http://%s/%s/default/user/login" % \
             (request.env.http_host, request.application)) 


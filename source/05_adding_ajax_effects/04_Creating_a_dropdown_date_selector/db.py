# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

if not request.env.web2py_runtime_gae:     
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite') 
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore') 
    ## store sessions and tickets there
    session.connect(request, response, db = db) 
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key()) 
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables() 

## configure email
mail=auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

def select_datewidget(field,value):
    MINYEAR = 2000
    MAXYEAR = 2020
    import datetime
    now = datetime.date.today()
    dtval = value or now.isoformat()
    year,month,day= str(dtval).split("-")
    dt = SQLFORM.widgets.string.widget(field,value)
    id = dt['_id']
    dayid = id+'__day'
    monthid = id+'__month'
    yearid = id+'__year'
    wrapperid = id+'__wrapper'
    wrapper = DIV(_id=wrapperid)
    day = SELECT([OPTION(str(i).zfill(2)) for i in range(1,32)],
                 value=day,_id=dayid)
    month = SELECT([OPTION(datetime.date(2008,i,1).strftime('%B'),
                           _value=str(i).zfill(2)) for i in range(1,13)],
                 value=month,_id=monthid)
    year = SELECT([OPTION(i) for i in range(MINYEAR,MAXYEAR)],
                 value=year,_id=yearid)
    jqscr = SCRIPT("""
      jQuery('#%s').hide();
      var curval = jQuery('#%s').val();
      if(curval) {
        var pieces = curval.split('-');
        jQuery('#%s').val(pieces[0]);
        jQuery('#%s').val(pieces[1]);
        jQuery('#%s').val(pieces[2]);
      }
      jQuery('#%s select').change(function(e) {
        jQuery('#%s').val(
           jQuery('#%s').val()+'-'+jQuery('#%s').val()+'-'+jQuery('#%s').val());
      });
    """ % (id,id,yearid,monthid,dayid,wrapperid,id,yearid,monthid,dayid))
    wrapper.components.extend([month,day,year,dt,jqscr])
    return wrapper

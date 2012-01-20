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
    session.connect(request, response, db=db)
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
mail = auth.settings.mailer
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
use_janrain(auth, filename='private/janrain.key')

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

#THIS IS FOR SELECT_OR_ADD
class SelectOrAdd(object):
    def __init__(self, controller=None, function=None, form_title=None, button_text=None, dialog_width=450):
        if form_title == None:
            self.form_title = T('Add New')
        else:
            self.form_title = T(form_title)
        if button_text == None:
            self.button_text = T('Add')
        else:
            self.button_text = T(button_text)
        self.dialog_width = dialog_width

        self.controller = controller
        self.function = function

    def widget(self, field, value):
        #generate the standard widget for this field
        from gluon.sqlhtml import OptionsWidget
        select_widget = OptionsWidget.widget(field, value)

        #get the widget's id (need to know later on so can tell receiving controller what to update)
        my_select_id = select_widget.attributes.get('_id', None)
        add_args = [my_select_id]
        #create a div that will load the specified controller via ajax
        form_loader_div = DIV(LOAD(c=self.controller, f=self.function, args=add_args, ajax=True), _id=my_select_id + "_dialog-form", _title=self.form_title)
        #generate the "add" button that will appear next the options widget and open our dialog
        activator_button = A(T(self.button_text), _class='button', _id=my_select_id + "_option_add_trigger")
        #create javascript for creating and opening the dialog
        js = 'jQuery( "#%s_dialog-form" ).dialog({autoOpen: false, show: "blind", hide: "explode", width: %s});' % (my_select_id, self.dialog_width)
        js += 'jQuery( "#%s_option_add_trigger" ).click(function() { jQuery( "#%s_dialog-form" ).dialog( "open" );return false;}); ' % (my_select_id, my_select_id)  # decorate our activator button for good measure
        js += 'jQuery(function() { jQuery( "#%s_option_add_trigger" ).button({text: true, icons: { primary: "ui-icon-circle-plus"} }); });' % (my_select_id)
        jq_script = SCRIPT(js, _type="text/javascript")

        wrapper = DIV(_id=my_select_id + "_adder_wrapper")
        wrapper.components.extend([select_widget, form_loader_div, activator_button, jq_script])
        return wrapper


add_option = SelectOrAdd(form_title=T("Add a new something"),
                                              controller="product",
                                              function="add_category",
                                              button_text=T("Add New"),
                                              dialog_width=600)

db.define_table('category',
    Field('name', 'string', notnull=True, unique=True),
    Field('description', 'text')
)

db.define_table('product',
    Field('category_id', db.category, requires=IS_IN_DB(db, 'category.id', 'category.name')),
    Field('name', 'string', notnull=True),
    Field('description', 'text'),
    Field('price', 'decimal(10,2)', notnull=True)
    )

db.product.category_id.widget = add_option.widget



#THIS IS FOR UPLOADJS
db.define_table('document',
    Field('filename', 'upload')
    )

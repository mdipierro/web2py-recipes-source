#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys

# import wxPython:
import wx

# import gui2py support -wxHTML FORM handling- (change the path!)
sys.path.append(r"/home/reingart/gui2py")
from gui2py.form import EVT_FORM_SUBMIT

# import web2py (change the path!)
sys.path.append(r"/home/reingart/web2py")
from gluon.dal import DAL, Field
from gluon.sqlhtml import SQLFORM
from gluon.html import INPUT, FORM, TABLE, TR, TD
from gluon.validators import IS_NOT_EMPTY, IS_EXPR, IS_NOT_IN_DB, IS_IN_SET
from gluon.storage import Storage

# create DAL connection (and create DB if not exists)
db=DAL('sqlite://guitest.sqlite',folder=None)

# define a table 'person' (create/aster as necessary)
person = db.define_table('person',
    Field('name','string', length=100),
    Field('sex','string', length=1),
    Field('active','boolean', comment="check!"),
    Field('bio','text', comment="resume (CV)"),
    )

# set sample validator (do not allow empty nor duplicate names)
db.person.name.requires = [IS_NOT_EMPTY(),
                           IS_NOT_IN_DB(db, 'person.name')]

db.person.sex.requires = IS_IN_SET({'M': 'Male', 'F': 'Female'})

# create the wxPython GUI application instance:
app = wx.App(False)

# create a testing frame (wx "window"):
f = wx.Frame(None, title="web2py/gui2py sample app")

# create the web2py FORM based on person table
form = SQLFORM(db.person)

# create the HTML "browser" window:
html = wx.html.HtmlWindow(f, style= wx.html.HW_DEFAULT_STYLE | wx.TAB_TRAVERSAL)
# convert the web2py FORM to XML and display it
html.SetPage(form.xml())

def on_form_submit(evt):
    "Handle submit button user action"
    global form
    print "Submitting to %s via %s with args %s"% (evt.form.action, evt.form.method, evt.args)
    if form.accepts(evt.args, formname=None, keepvalues=False, dbio=False):
        print "accepted!"
        # insert the record in the table (if dbio=True this is done by web2py):
        db.person.insert(name=form.vars.name,
                         sex=form.vars.sex,
                         active=form.vars.active,
                         bio=form.vars.bio,
                        )
        # don't forget to commit, we aren't inside a web2py controller!
        db.commit()
    elif form.errors:
        print "errors", form.errors
    # refresh the from (show web2py errors)
    html.SetPage(form.xml())

# connect the FORM event with the HTML browser
html.Bind(EVT_FORM_SUBMIT, on_form_submit)

# show the main window
f.Show()
# start the wx main-loop to interact with the user
app.MainLoop() 

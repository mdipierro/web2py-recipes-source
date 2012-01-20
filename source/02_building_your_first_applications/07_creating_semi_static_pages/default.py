# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index(): return flatpage()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def setup_flatpage():
    if not db(db.flatpage).count():
        db.flatpage.insert(title="Home", subtitle="Main Index", 
        c="default", f='index', body="<h3>Hello world!</h3>")
        db.flatpage.insert(title="About us", subtitle="The company",
        c="company", f='about_us', body="<h3>My company!</h3>")
        db.flatpage.insert(title="Mision & Vision", subtitle="The company", 
        c="company", f='mision_vision', body="<h3>Our vision is...</h3>")
        db.flatpage.insert(title="Our Team", subtitle="Who we are", 
        c="company", f='our_team', body="<h1>We are...</h3>")
        db.flatpage.insert(title="Contact Us", subtitle="Where we are",
        c="company", f='contact_us', body="<h3>Contact form:...</h3>")
    return "Flatpages has %s records" % db(db.flatpage).count()

# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    return dict(message=T('Hello World'))

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

def setup_navbar():
    if not db(db.navbar).count():
        # create default index entry:
        home_id = db.navbar.insert(title="Home", c="default")
    
        # create a "Company" leaf with typical options:
        company_id = db.navbar.insert(title="Company", c="company")
        db.navbar.insert(title="About Us", f='about_us',
                     parent_id=company_id)
        db.navbar.insert(title="Mision & Vision", f='mision_vision',
                     parent_id=company_id)
        db.navbar.insert(title="Our Team", f='our_team',
                     parent_id=company_id)
    
        products_id = db.navbar.insert(title="Products", c="products")
        # Add some "Computers models" to products entry:
        computers_id = db.navbar.insert(title="Computers", f='computers',
                                    parent_id=products_id)
        for model in 'basic', 'pro', 'gamer':
            db.navbar.insert(title="Model %s" % model, args=model, 
                         parent_id=computers_id)
    return "There are %s navigation bar items" % db(db.navbar).count()

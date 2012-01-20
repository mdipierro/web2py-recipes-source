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
    
    def mylink(field, type, ref):
        return URL(c="default", f="edit_bottle", args=[field])
    
    if db(db.bottle).count() <= 0:
        db.bottle.insert(name="old", year="1000")
    return dict(bottles = SQLTABLE(db(db.bottle).select(), linkto=mylink))

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


def edit_bottle():
    bottle_id = request.args(0)
    bottle = db.bottle(bottle_id) or redirect(URL('error'))
    bottle_tasters = db(db.taster.bottle==bottle_id).select()
    tasters, actual_testers = range(10), len(bottle_tasters)
    form=SQLFORM.factory(
       Field('name', default=bottle.name),
       Field('year', 'integer', default=bottle.year),
       *[Field('taster%i'%i,db.auth_user,
               default=bottle_tasters[i].auth_user if i<actual_testers else '',
               label=T('Taster #%i'%i)) for i in tasters])
    if form.accepts(request,session):
        bottle.update_record(**db.bottle._filter_fields(form.vars))
        db(db.taster.bottle==bottle_id).delete()
        for i in tasters:            
            if 'taster%i'%i in form.vars: 
                db.taster.insert(auth_user=form.vars['taster%i'%i],bottle=bottle_id)
        response.flash = 'Wine and guest data are now updated'
    return dict(form=form)

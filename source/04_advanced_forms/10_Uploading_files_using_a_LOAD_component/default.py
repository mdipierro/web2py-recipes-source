# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

print request.function, request.vars.keys()

def index():
    db(db.document).delete()
    return dict()

@auth.requires_signature()
def component_list():
    db.document.filename.represent = lambda f,r: f and A('file',_href=URL('download',args=f))
    return db(db.document).select()

@auth.requires_signature()
def component_form():
    db.document.uploaded_by.default = auth.user_id
    db.document.uploaded_by.writable = False
    form = SQLFORM(db.document)
    if form.accepts(request):
        response.flash = 'Thanks for filling the form'
        response.js = "web2py_component('%s','doc_list');" % \
            URL('component_list.load',user_signature=True)
    elif form.errors:
        response.flash = 'Fill the form correctly'
    else:
        response.flash = 'Please fill the form'
    return dict(form=form)

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

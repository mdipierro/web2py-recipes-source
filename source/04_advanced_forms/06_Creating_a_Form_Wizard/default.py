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
    redirect(URL(f="wizard"))

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


def wizard():
    STEPS = {0: ('field1', 'field2'), # fields for 1st page
             1: ('field3', 'field4'), # fields for 2nd page
             2: ('field5', 'field6'), # fields for 2nd page
             3: URL('done')} # url when wizard completed
    step = int(request.args(0) or 0)
    if not step in STEPS: redirect(URL(args=0))
    fields = STEPS[step]
    print "Fields: " + str(fields) + " Step " + str(step)
    if step==0: 
        session.wizard = {}
    if isinstance(fields,tuple):
        form = SQLFORM.factory(*[f for f in db.mytable if f.name in fields])
        if form.accepts(request,session):
            session.wizard.update(form.vars)
            redirect(URL(args=step+1))            
    else:
        db.mytable.insert(**session.wizard)
        session.flash = T('wizard completed')
        redirect(fields)
    return dict(form=form,step=step)

def done():
    return dict(message="End of wizard", back=A("New wizard", _href=URL("wizard")))

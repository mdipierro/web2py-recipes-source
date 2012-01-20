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
    message = "Send e-mail form"
    form = SQLFORM.factory(
                           Field("source", comment='myemail@address.com'),
                           Field("subject", comment='Subject'),
                           Field("body","text"),
                           Field("to_addresses", comment='recipient@email.com'),
                           Field("cc_addresses"),
                           Field("bcc_addresses"),
                           Field("format", comment='text'),
                           Field("reply_addresses"),
                           Field("return_path")
                           )
    if form.accepts(request.vars, session):
        try:
            message = test_send_emails(request.vars)
        except Exception, e:
            message = str(e)
            
    return dict(form = form, message = message)

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

def test_send_emails(vars):
    aws_key = 'YOUR_AWS_KEY'
    aws_secret_key = 'YOUR_SECRET_KEY'
    from boto.ses.connection import SESConnection
    conn = SESConnection(aws_key, aws_secret_key)
    return conn.send_email(source=vars.source,
                           subject=vars.subject, 
                           body=vars.body,
                           to_addresses=vars.to_addresses,
                           cc_addresses=vars.cc_addresses,
                           bcc_addresses=vars.bcc_addresses,
                           format=vars.format,
                           reply_addresses=vars.reply_addresses,
                           return_path=vars.return_path)

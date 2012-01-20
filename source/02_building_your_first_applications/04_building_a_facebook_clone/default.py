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


def index():
    if auth.user: redirect(URL('home'))
    return locals()

def user():
    return dict(form=auth())

def download():
    return response.download(request, db)

def call():
    session.forget()
    return service()

# our home page, will show our posts and posts by friends
@auth.requires_login()
def home():
    Post.posted_by.default = me
    Post.posted_on.default = request.now
    crud.settings.formstyle = 'table2cols'
    form = crud.create(Post)
    friends = [me]+[row.target for row in myfriends.select(Link.target)]
    posts = db(Post.posted_by.belongs(friends))\
        .select(orderby=~Post.posted_on, limitby=(0, 100))
    return locals()

# our wall will show our profile and our own posts
@auth.requires_login()
def wall():
    user = User(a0 or me)
    if not user or not (user.id==me or \
       myfriends(Link.target==user.id).count()):
        redirect(URL('home'))
    posts = db(Post.posted_by==user.id)\
        .select(orderby=~Post.posted_on, limitby=(0, 100))
    return locals()

# a page for searching friends and requesting friendship
@auth.requires_login()
def search():
    form = SQLFORM.factory(Field('name', requires=IS_NOT_EMPTY()))
    if form.accepts(request):
        tokens = form.vars.name.split()
        query = reduce(lambda a,b:a&b,
            [User.first_name.contains(k)|User.last_name.contains(k) \
             for k in tokens])
        people = db(query).select(orderby=alphabetical)
    else:
        people = []
    return locals()

# a page for accepting and denying friendship requests
@auth.requires_login()
def friends():
    friends = db(User.id==Link.source)(Link.target==me)\
      .select(orderby=alphabetical)
    requests = db(User.id==Link.target)(Link.source==me)\
      .select(orderby=alphabetical)
    return locals()

# this is the Ajax callback
@auth.requires_login()
def friendship():
    """Ajax callback!"""
    if request.env.request_method != 'POST': raise HTTP(400)
    if a0=='request' and not Link(source=a1, target=me):
        # insert a new friendship request
        Link.insert(source=me, target=a1)
    elif a0=='accept':
        # accept an existing friendship request
        db(Link.target==me)(Link.source==a1).update(accepted=True)
        if not db(Link.source==me)(Link.target==a1).count():
            Link.insert(source=me, target=a1)
    elif a0=='deny':
        # deny an existing friendship request
        db(Link.target==me)(Link.source==a1).delete()
    elif a0=='remove':
        # delete a previous friendship request
        db(Link.source==me)(Link.target==a1).delete()

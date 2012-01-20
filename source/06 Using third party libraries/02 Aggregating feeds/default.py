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
    redirect("planet")
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

def planet():
    FILTER = 'web2py'
    import datetime
    import re
    import gluon.contrib.rss2 as rss2
    import gluon.contrib.feedparser as feedparser

    # filter for general (not categorized) feeds
    regex =  re.compile(FILTER,re.I)
    # select all feeds
    feeds = db(db.feed).select()
    entries = []
    for feed in feeds:
        # fetch and parse feeds
        d = feedparser.parse(feed.url)
        for entry in d.entries:
            # filter feed entries
            if not feed.general or regex.search(entry.description):
                # extract entry attributes
                entries.append({
                    'feed': {'author':feed.author,
                             'link':feed.link,
                             'url':feed.url,
                             'name':feed.name},
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.description,
                    'author': hasattr(entry, 'author_detail') \
                              and entry.author_detail.name \
                              or feed.author,
                    'date': datetime.datetime(*entry.date_parsed[:6])
                })
    # sort entries by date, descending
    entries.sort(key=lambda x: x['date'],reverse=True)
    now = datetime.datetime.now()
    # aggregate rss2 feed with parsed entries
    rss = rss2.RSS2(title="Planet web2py",
       link = URL("planet").encode("utf8"),
       description = "planet author",
       lastBuildDate = now,
       items = [
          rss2.RSSItem(
            title = entry['title'],
            link = entry['link'],
            description = entry['description'],
            author = entry['author'],
            # guid = rss2.Guid('unknown'),
            pubDate = entry['date']) for entry in entries]
       )

    # return new rss feed xml
    response.headers['Content-Type']='application/rss+xml'
    return rss2.dumps(rss)

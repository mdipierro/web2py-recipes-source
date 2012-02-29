# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def links_right(tablerow,rowtype,rowdata):
    if rowtype != 'pager':
        links = tablerow.components[:3]
        del tablerow.components[:3]
        tablerow.components.extend(links)


def on_row_created(row,rowtype,record):
    if rowtype=='header':
        row.components.append(TH(' '))

if request.controller == 'default' and request.function == 'data':
    if request.args:
        crud.settings[request.args(0)+'_next'] = URL('index')

def index():
    """
grid.datasource = db(db.stuff.id>0)               # Set
grid.datasource = db(db.stuff.id>0).select()      # Rows
grid.datasource = db.stuff                        # Table
grid.datasource = [db.stuff,db.others]            # list of Tables
grid.datasource = db(db.stuff.id==db.other.thing) # join
    """
    
    import webgrid
    grid = webgrid.WebGrid(crud)
    grid.datasource = db(db.stuff.id>0)
    grid.pagesize = 10

    grid.enabled_rows = ['header','filter', 'pager','totals','footer','add_links']

    grid.crud_function = 'data'

    grid.fields = ['stuff.name','stuff.location','stuff.quantity']
    
    grid.field_headers = ['Name','Location','Quantity']

    grid.action_links = ['view','edit','delete']
    grid.action_headers = ['view','edit','delete']

    grid.totals = ['stuff.quantity']    

    grid.filters = ['stuff.name','stuff.created']

    grid.allowed_vars = ['pagesize','pagenum','sortby','ascending','groupby','totals']

    """
grid.view_link = lambda row: ...
grid.edit_link = lambda row: ...
grid.delete_link = lambda row: ...
grid.header = lambda fields: ...
grid.datarow = lambda row: ...
grid.footer = lambda fields: ...
grid.pager = lambda pagecount: ...
grid.page_total = lambda:
    """

    """
    grid.joined # tells you if your datasource is a join
grid.css_prefix # used for css
grid.tablenames
grid.response # the datasource result
grid.colnames # column names of datasource result
grid.pagenum
grid.pagecount
grid.total # the count of datasource result
    """

    grid.footer = lambda fields : TFOOT(TD("This is my footer" ,
    _colspan=len(grid.action_links)+len(fields),
    _style="text-align:center;"),
    _class=grid.css_prefix + '-webgrid footer')

    grid.messages.confirm_delete = 'Are you sure?'
    grid.messages.no_records = 'No records'
    grid.messages.add_link = '[add %s]'
    grid.messages.page_total = "Total:"

    grid.row_created = on_row_created

    grid.row_created = links_right
    
    return dict(grid=grid()) # notice the ()

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


# @auth.requires_signature()
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

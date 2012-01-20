# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def process_ipn(ipn_msg_id,param):
  """
  We process the parameters sent from IPN PayPal, to correctly store the confirmed sales
  in the database.

  param -- request.vars from IPN message from PayPal
  """
  # Check if transaction_id has already been processed.
  query1 = db.ipn_msgs.trans_id==param['txn_id']
  query2 = db.ipn_msgs.processed == True
  rows = db(query1 & query2).select()
  if not rows:
    trans = param['txn_id']
    payer_email = param['payer_email']
    n_items = int(param['num_cart_items'])
    pay_date = param['payment_date']
    total = param['mc_gross']
    curr = param['mc_currency']
    event_code = param['custom']
    if param.has_key('memo'): memo=param['memo']
    event_id = db(db.event.code==event_code).select(db.event.id)
    if not event_id:
      db.ipn_msgs[ipn_msg_id]=dict(security_msg=T('Event does not exist'))
    else:
      error=False
      for i in range(1,n_items+1):
        product_code = param['item_number'+str(i)]
        qtty = param['quantity'+str(i)]
        line_total = float(param['mc_gross_'+str(i)]) + float(param['mc_tax'+str(i)])
        product=db(db.product.ext_code==product_code).select(db.product.id)
        if not product:
          db.ipn_msgs[ipn_msg_id]=dict(security_msg=T('Product code does not exist'))
          error=True
        else:
          db.glist.insert(event=event_id[0],product=product[0],buyer=payer_email,transact=trans,
              purchase_date=pay_date,quantity_sold=qtty,price=line_total,observations=memo)
      if not error: db.ipn_msgs[ipn_msg_id]=dict(processed=True)        
      

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

import datetime
import string

if not session.cart: session.cart, session.balance={},0
app=request.application

#### Setup PayPal login email (seller id) in the session
#### I store paypal_id in a table
session.paypal_id="my_paypal_id" # myorg.paypal_id
import urllib2, urllib
import datetime

class Connection:
  def __init__(self, base_url, username, password, realm = None, header = {}):
    self.base_url = base_url
    self.username = username
    self.password = password
    self.realm    = realm
    self.header   = header

  def request(self, resource, data = None, args = None):
    path = resource

    if args:
      path += "?" + (args)

    # create a password manager
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

    if self.username and self.password:
      # Add the username and password.
      password_mgr.add_password(self.realm, self.base_url, self.username, self.password)

    handler = urllib2.HTTPBasicAuthHandler(password_mgr)

    # create "opener" (OpenerDirector instance)
    opener = urllib2.build_opener(handler)

    # Install the opener.
    # Now all calls to urllib2.urlopen use our opener.
    urllib2.install_opener(opener)
    #Create a Request
    req=urllib2.Request(self.base_url + path, data, self.header)
    # use the opener to fetch a URL
    error = ''
    try:
      ret=opener.open(req)
    except urllib2.HTTPError, e:
      ret = e
      error = 'urllib2.HTTPError'
    except urllib2.URLError, e:
      ret = e
      error = 'urllib2.URLError'

    return ret, error

def add_to_cart():
  """
  Add data into the session.cart dictionary
  Session.cart is a dictionary with id product_id and value = quantity
  Session.balance is a value with the total of the transaction.
  After updating values, redirect to checkout
  """
  pid=request.args[0]
  product=db(db.product.id==pid).select()[0]
  product.update_record(clicked=product.clicked+1)
  try: qty=session.cart[pid]+1
  except: qty=1
  session.cart[pid]=qty
  session.balance+=product.price
  redirect(URL('checkout'))

def remove_from_cart():
  """
  allow add to cart
  """
  pid = request.args[0]
  product=db(db.product.id==pid).select()[0]
  if session.cart.has_key(pid):
      session.balance-=product.price
      session.cart[pid]-=1
      if not session.cart[pid]: del session.cart[pid]
  redirect(URL('checkout'))

def empty_cart():
  """
  allow add to cart
  """
  session.cart, session.balance={},0
  redirect(URL('checkout'))

def checkout():
  """
  Checkout
  """
  pids = session.cart.keys()
  cart={}
  products={}
  for pid in pids:
    products[pid]=db(db.product.id==pid).select()[0]
  return dict(products=products,paypal_id=session.paypal_id)
  
def confirm():
  """
  This is set so as to capture the transaction data from PayPal
  It captures the transaction ID from the HTTP GET that PayPal sends.
  And using the token from vendor profile PDT, it does a form post.
  The data from the http get comes as vars Name Value Pairs.
  """
  if request.vars.has_key('tx'):
    trans = request.vars.get('tx')
    # Establish connection.
    conn = Connection(base_url=protocol+domain, username=user, password = passwd, realm = realm, header = headers)
    data = "cmd=_notify-synch&tx="+trans+"&at="+paypal_token
    resp,error=conn.request('/cgi-bin/webscr', data)
    data={}
    if error=='':
      respu = resp.read()
      respuesta = respu.splitlines()
      data['status']=respuesta[0]
      if respuesta[0]=='SUCCESS':
        for r in respuesta[1:]:
          key,val = r.split('=')
          data[key]=val
        msg=''
        if data.has_key('memo'): msg=data['memo']
        form = FORM("Quiere dejar un mensaje con los regalos?",
            INPUT(_name=T('message'),_type="text",_value=msg),
            INPUT(_type="submit"))
        if form.accepts(request,session):
          email=data['payer_email'].replace('%40','@')
          id = db.gift_msg.insert(buyer=data['payer_email'],transact=trans,msg=form.vars.message)
          response.flash=T('Your message will be passed on to the recipient')
          redirect(URL('index'))

        return dict(data=data,form=form)
      return dict(data=data)
    else:
      data['status']='FAIL'
  else:
    redirect(URL('index'))
  return dict(trans=trans)

def ipn_handler():
  """
  Manages the ipn connection with PayPal
  Ask PayPal to confirm this payment, return status and detail strings
  """
  parameters = None
  parameters =  request.vars
  if parameters:
    parameters['cmd'] = '_notify-validate'
    params = urllib.urlencode(parameters)
    conn = Connection(base_url=protocol+domain, username=user, password = passwd, realm = realm, header = headers)
    resp,error =conn.request('/cgi-bin/webscr', params)
    timestamp=datetime.datetime.now()
    # We are going to log all messages confirmed by PayPal.
    if error =='':
      ipn_msg_id = db.ipn_msgs.insert(trans_id=parameters['txn_id'],timestamp=timestamp,type=resp.read(),msg=params,
        total=parameters['mc_gross'],fee=parameters['mc_fee'],currency=parameters['mc_currency'])
      # But only interested in processing messages that have payment status completed and are VERIFIED by PayPal.
      if parameters['payment_status']=='Completed':
        process_ipn(ipn_msg_id,parameters)

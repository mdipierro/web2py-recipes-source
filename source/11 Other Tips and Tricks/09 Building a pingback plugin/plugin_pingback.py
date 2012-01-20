#!/usr/bin/env python
# coding: utf8
#
# Author:  Hans Christian v. Stockhausen <hc at vst.io>
# Date:    2010-12-19
# License: MIT
#
# TODO
# - Check entity expansion requirements (e.g. &lt;) as per Pingback spec page 7
# - make try-except-finally in PingbackClient.ping robust

import httplib
import logging
import urllib2
import xmlrpclib
from gluon.html import URL

__author__ = 'H.C. v. Stockhausen <hc at vst.io>'
__version__ = '0.1.1'

from gluon import *

# we2py specific constants
TABLE_PINGBACKS = 'plugin_pingback_pingbacks'

# Pingback protocol faults
FAULT_GENERIC = 0
FAULT_UNKNOWN_SOURCE = 16
FAULT_NO_BACKLINK = 17
FAULT_UNKNOWN_TARGET = 32
FAULT_INVALID_TARGET = 33
FAULT_ALREADY_REGISTERED = 48
FAULT_ACCESS_DENIED = 49
FAULT_UPSTREAM_ERROR = 50

def define_table_if_not_done(db):
    if not TABLE_PINGBACKS in db.tables:
       db.define_table(TABLE_PINGBACKS,
          Field('source', notnull=True),
          Field('target', notnull=True),
          Field('direction', notnull=True,
             requires=IS_IN_SET(('inbound', 'outbound'))),
          Field('status'), # only relevant for outbound pingbacks
          Field('datetime', 'datetime', default=current.request.now))

class PingbackServerError(Exception):
    pass

class PingbackClientError(Exception):
    pass

class PingbackServer(object):
    " Handles incomming pingbacks from other sites. "

    def __init__(self, db, request, callback=None):
        self.db = db
        self.request = request
        self.callback = callback
        define_table_if_not_done(db)

    def __call__(self):
        """
        Invoked instead of the decorated function if the request is a pingback
        request from some external site.
        """

        try:
            self._process_request()
        except PingbackServerError, e:
            resp = str(e.message)
        else:
            resp = 'Pingback registered'
        return xmlrpclib.dumps((resp,))

    def _process_request(self):
        " Decode xmlrpc pingback request and process it "

        (self.source, self.target), method = xmlrpclib.loads(
            self.request.body.read())
        if method != 'pingback.ping':
            raise PingbackServerError(FAULT_GENERIC)
        self._check_duplicates()
        self._check_target()
        self._check_source()
        if self.callback:
            self.callback(self.source, self.target, self.html)
        self._store_pingback()

    def _check_duplicates(self):
        " Check db whether the pingback request was previously processed "

        db = self.db
        table = db[TABLE_PINGBACKS]
        query = (table.source==self.source) & (table.target==self.target)
        if db(query).select():
            raise PingbackServerError(FAULT_ALREADY_REGISTERED)

    def _check_target(self):
        " Check that the target URI exists and supports pingbacks "

        try:
            page = urllib2.urlopen(self.target)
        except:
            raise PingbackServerError(FAULT_UNKNOWN_TARGET)
        if not page.info().has_key('X-Pingback'):
            raise PingbackServerError(FAULT_INVALID_TARGET)

    def _check_source(self):
        " Check that the source URI exists and contains the target link "

        try:
            page = urllib2.urlopen(self.source)
        except:
            raise PingbackServerError(FAULT_UNKNOWN_SOURCE)
        html = self.html = page.read()
        target = self.target
        try:
            import BeautifulSoup2
            soup = BeautifulSoup.BeautifulSoup(html)
            exists = any([a.get('href')==target for a in soup.findAll('a')])
        except ImportError:
            import re
            logging.warn('plugin_pingback: Could not import BeautifulSoup,' \
                ' using re instead (higher risk of pingback spam).')
            pattern = r'<a.+href=[\'"]?%s[\'"]?.*>' % target
            exists = re.search(pattern, html) != None
        if not exists:
            raise PingbackServerError(FAULT_NO_BACKLINK)

    def _store_pingback(self):
        " Companion method for _check_duplicates to suppress duplicates. "

        self.db[TABLE_PINGBACKS].insert(
            source=self.source,
            target=self.target,
            direction='inbound')

class PingbackClient(object):
    " Notifies other sites about backlinks. "

    def __init__(self, db, source, targets, commit):
        self.db = db
        self.source = source
        self.targets = targets
        self.commit = commit
        define_table_if_not_done(db)

    def ping(self):
        status = 'FIXME'
        db = self.db
        session = current.session
        response = current.response
        table = db[TABLE_PINGBACKS]
        targets = self.targets
        if isinstance(targets, str):
            targets = [targets]
        for target in targets:
            query = (table.source==self.source) & (table.target==target)
            if not db(query).select(): # check for duplicates
                id_ = table.insert(
                    source=self.source,
                    target=target,
                    direction='outbound')
                if self.commit:
                    db.commit()
                try:
                    server_url = self._get_pingback_server(target)
                except PingbackClientError, e:
                    status = e.message
                else:
                    try:
                        session.forget()
                        session._unlock(response)
                        server = xmlrpclib.ServerProxy(server_url)
                        status = server.pingback.ping(self.source, target)
                    except xmlrpclib.Fault, e:
                        status = e
                finally:
                    db(table.id==id_).update(status=status)

    def _get_pingback_server(self, target):
        " Try to find the target's pingback xmlrpc server address "

        # first try to find the pingback server in the HTTP header
        try:
            host, path = urllib2.splithost(urllib2.splittype(target)[1])
            conn = httplib.HTTPConnection(host)
            conn.request('HEAD', path)
            res = conn.getresponse()
            server = dict(res.getheaders()).get('x-pingback')
        except Exception, e:
            raise PingbackClientError(e.message)
        # next try the header with urllib in case of redirects
        if not server:
            page = urllib2.urlopen(target)
            server = page.info().get('X-Pingback')
        # next search page body for link element
        if not server:
            import re
            html = page.read()
            # pattern as per Pingback 1.0 specification, page 7
            pattern = r'<link rel="pingback" href=(P<url>[^"])" ?/?>'
            match = re.search(pattern, html)
            if match:
                server = match.groupdict()['url']
        if not server:
            raise PingbackClientError('No pingback server found.')
        return server

def listen(db, callback=None):
    """
    Decorator for page controller functions that want to support pingbacks.
    The optional callback parameter is a function with the following signature.
    callback(source_uri, target_uri, source_html)
    """

    request = current.request
    response = current.response

    def pingback_request_decorator(_):
        return PingbackServer(db, request, callback)

    def standard_request_decorator(controller):
        def wrapper():
            " Add X-Pingback HTTP Header to decorated function's response "

            url_base = '%(wsgi_url_scheme)s://%(http_host)s' % request.env
            url_path = URL(args=['x-pingback'])
            response.headers['X-Pingback'] = url_base + url_path
            return controller()
        return wrapper

    if request.args(0) in ('x-pingback', 'x_pingback'):
        return pingback_request_decorator
    else:
        return standard_request_decorator

def ping(db, source, targets, commit=True):
    " Notify other sites of backlink "

    client = PingbackClient(db, source, targets, commit)
    client.ping()


    
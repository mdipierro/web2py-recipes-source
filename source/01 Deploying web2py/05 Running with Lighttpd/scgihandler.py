#!/usr/bin/env python
# -*- coding: utf-8 -*-

LOGGING = False
SOFTCRON = False

import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
sys.path = [path]+[p for p in sys.path if not p==path]

import gluon.main

if LOGGING:
    application = gluon.main.appfactory(
        wsgiapp=gluon.main.wsgibase,
        logfilename='httpserver.log',
        profilerfilename=None)
else:
    application = gluon.main.wsgibase

if SOFTCRON:
    from gluon.settings import global_settings
    global_settings.web2py_crontype = 'soft'

try:
    import paste.util.scgiserver as scgi
    scgi.serve_application(application, '', 4000).run()
except ImportError:
    from wsgitools.scgi.forkpool import SCGIServer
    SCGIServer(application, port=4000).run()

    

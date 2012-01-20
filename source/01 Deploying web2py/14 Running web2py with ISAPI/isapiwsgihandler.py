# -*- coding: utf-8 -*-
# The entry point for the ISAPI extension.
def __ExtensionFactory__():
    import os
    import sys
    path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(path)
    sys.path = [path]+[p for p in sys.path if not p==path]
    import gluon.main
    import isapi_wsgi
    application=gluon.main.wsgibase
    return isapi_wsgi.ISAPIThreadPoolHandler(application)

# ISAPI installation:
if __name__=='__main__':
    from isapi.install import ISAPIParameters
    from isapi.install import ScriptMapParams
    from isapi.install import VirtualDirParameters
    from isapi.install import HandleCommandLine

    params = ISAPIParameters()
    sm = [
       ScriptMapParams(Extension="*", Flags=0)
    ]
    vd = VirtualDirParameters(Name="appname",
                              Description = "Web2py in Python",
                              ScriptMaps = sm,
                              ScriptMapUpdate = "replace")
    params.VirtualDirs = [vd]
    HandleCommandLine(params)


# coding: utf8
# intente algo como
def index(): return dict(message="hello from rpc.py")

from gluon.tools import Service
service = Service(globals())

def call():
    session.forget()
    return service()

@service.amfrpc3("mydomain")
def test():
    return "Test!!!"

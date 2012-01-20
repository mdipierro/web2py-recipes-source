# coding: utf8
# intente algo como
def index(): return dict(message="hello from sample.py")

@service.xmlrpc
@service.soap('AddStrings',returns={'AddResult':str},args={'a':str, 'b':str})
@service.soap('AddIntegers',returns={'AddResult':int},args={'a':int, 'b':int})
def add(a,b): 
    "Add two values"
    return a+b

@service.xmlrpc
@service.soap('SubIntegers',returns={'SubResult':int},args={'a':int, 'b':int})
def sub(a,b): 
    "Substract two values"
    return a-b

def call():
    return service()

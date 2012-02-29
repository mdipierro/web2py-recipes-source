# coding: utf8
# intente algo como
def index(): return dict(message="hello from BasicJSONRPCData.py")

import math
from gluon.tools import Service
service = Service(globals())

def call():
    return service()

@service.jsonrpc
def systemListMethods():
    #Could probably be rendered dynamically
    return ["SmallTest", "BiggerTest"];

@service.jsonrpc
def SmallTest(a, b):
    return a + b

@service.jsonrpc
def BiggerTest(a, b):
    results = dict()
    results["originalValues"] = [a,b]
    results["sum"] = a + b
    results["difference"] = a - b
    results["product"] = a * b
    results["quotient"] = float(a)/b
    results["power"] = math.pow(a,b)
    return results

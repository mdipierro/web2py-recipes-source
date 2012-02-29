# coding: utf8
# intente algo como
def index(): return dict(message="hello from images.py")

def border_radius():
    import re
    radius = int(request.vars.r or 5)
    color = request.vars.fg or 'rbg(249,249,249)'
    if re.match('\d{3},\d{3},\d{3}',color):
        color = 'rgb(%s)' % color
    bg = request.vars.bg or 'rgb(235,232,230)'
    if re.match('\d{3},\d{3},\d{3}',bg):
        bg = 'rgb(%s)'%bg
    import gluon.contenttype
    
    response.headers['Content-Type']= 'image/svg+xml;charset=utf-8'
    return '''<?xml version="1.0" ?><svg xmlns="http://www.w3.org/2000/svg"><rect fill="%s" x="0" y="0" width="100%%" height="100%%" /><rect ill="%s" x="0" y="0" width="100%%" height="100%%" rx="%spx" /></svg>'''%(bg,color,radius)

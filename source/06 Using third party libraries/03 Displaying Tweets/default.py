# -*- coding: utf-8 -*-

def index():
    response.files.append(URL("static","css/tweets.css"))
    response.flash = T('You are successfully running web2py.')
    return dict(message=T('Hello World'))

@cache(request.env.path_info,time_expire=60*15,cache_model=cache.ram)
def twitter():
    session.forget()
    session._unlock(response)
    import gluon.tools
    import gluon.contrib.simplejson as sj
    try:
        if TWITTER_HASH:
            page = gluon.tools.fetch('http://twitter.com/%s?format=json'%TWITTER_HASH)
            return sj.loads(page)['#timeline']
        else:
            return 'disabled'
    except Exception, e:
        return DIV(T('Unable to download because:'),BR(),str(e))

def user():
    return dict(form=auth())


def download():
    return response.download(request,db)


def call():
    session.forget()
    return service()

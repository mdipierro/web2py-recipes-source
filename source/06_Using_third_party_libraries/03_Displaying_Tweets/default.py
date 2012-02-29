# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

TWITTER_HASH = "web2py"

def index():
    response.files.append(URL("static","css/tweets.css"))
    return dict(TWITTER_HASH=TWITTER_HASH)

@cache(request.env.path_info,time_expire=60*15,cache_model=cache.ram)
def twitter():
  session.forget()
  session._unlock(response)
  import gluon.tools
  import gluon.contrib.simplejson as sj
  try:
    if TWITTER_HASH:
      page = gluon.tools.fetch(' http://search.twitter.com/search.json?q=%%40%s' 
        % TWITTER_HASH)
      data = sj.loads(page, encoding="utf-8")['results']
      d = dict()
      for e in data:
          d[e["id"]] = e
      r = reversed(sorted(d))
      return dict(tweets = [d[k] for k in r])
    else:
      return 'disabled'
  except Exception, e:
    return DIV(T('Unable to download because:'),BR(),str(e))

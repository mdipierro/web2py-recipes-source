# coding: utf8

def plugin_feedreader(name, source='google-group'):
    """parse group feeds"""
    from gluon.contrib import feedparser
    if source=='google-group':
        URL = "http://groups.google.com/group/%(name)s/feed/rss_v2_0_msgs.xml" 
    elif source=='google-code':
        URL = "http://code.google.com/feeds/p/%(name)s/hgchanges/basic"
    else:
        URL = source
    url = URL % dict(name=name)
    g = feedparser.parse(url)
    html = UL(*[LI(A(entry['title'],_href=entry['link']))\
                for entry in g['entries'][0:5]])
    return XML(html)

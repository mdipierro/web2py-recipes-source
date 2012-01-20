# coding: utf8
def plugin_flickr(key, photoset=None, per_page=15, page=1):
    from urllib2 import urlopen
    from xml.dom.minidom import parse as domparse
    apiurl = 'http://api.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key=%(apikey)s&photoset_id=%(photoset)s&privacy_filter=1&per_page=%(per_page)s&page=%(page)s&extras=url_t,url_m,url_o,url_sq'
    dom = domparse(urlopen(apiurl % dict(photoset=photoset, per_page=per_page, page=page, apikey=key)))
    
    print dom.toxml()

    photos = []

    for node in dom.getElementsByTagName('photo'):
        photos.append({
            'id':node.getAttribute('id'),
            'title':node.getAttribute('title'),
            'thumb':node.getAttribute('url_t'),
            'medio':node.getAttribute('url_m'),
            'original':node.getAttribute('url_o'),
                    'square':node.getAttribute('url_sq'),
            })

    return photos

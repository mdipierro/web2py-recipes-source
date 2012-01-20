# coding: utf8
import os

def plugin_detect_mobile(switch_view=True):
    from mobile.sniffer.detect import detect_mobile_browser
    if detect_mobile_browser(request.env.http_user_agent):
        if switch_view:
            view = '%(controller)s/%(function)s.mobile.%(extension)s' % request
            if os.path.exists(os.path.join(request.folder, 'views',view)):
                response.view = view
                return True
    return False
plugin_detect_mobile()

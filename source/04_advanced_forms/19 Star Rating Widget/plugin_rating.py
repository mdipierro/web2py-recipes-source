# coding: utf8

DEPENDENCIES = [
  'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.9/jquery-ui.js',
  'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.9/themes/ui-darkness/jquery-ui.css',
  URL(c='static/stars',f='jquery.ui.stars.js'),
  URL(c='static/stars',f='jquery.ui.stars.css')]

def rating_widget(f,v):
    from gluon.sqlhtml import OptionsWidget
    import uuid
    id = str(uuid.uuid4())
    for path in DEPENDENCIES:
        response.files.append(path)
    return DIV(SPAN(_id="stars-cap"),
               DIV(OptionsWidget.widget(f,v),_id=id),
               SCRIPT("jQuery(function(){jQuery('#%s').stars({inputType: 'select'});});" % id))

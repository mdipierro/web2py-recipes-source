# coding: utf8


def slider_widget(field,value):
    response.files.append("http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.9/jquery-ui.js")
    response.files.append("http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.9/themes/ui-darkness/jquery-ui.css")
    id = '%s_%s' % (field._tablename,field.name)
    wrapper = DIV(_id="slider_wrapper",_style="width: 200px;text-align:center;")
    wrapper.append(DIV(_id=id+'__slider'))
    wrapper.append(SPAN(INPUT(_id=id, _style="display: none;"), _id=id+'__value'))
    wrapper.append(SQLFORM.widgets.string.widget(field,value))
    wrapper.append(SCRIPT("""
        jQuery('#%(id)s__value').text('%(value)s');
        jQuery('#%(id)s').val('%(value)s');
        jQuery('#%(id)s').hide();        
        jQuery('#%(id)s__slider').slider({
        value:'%(value)s', 
        stop: function(event, ui){
        jQuery('#%(id)s__value').text(ui.value);
        jQuery('#%(id)s').val(ui.value);
        }});
        """ % dict(id=id, value=value)))
    return wrapper

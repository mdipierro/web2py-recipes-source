# coding: utf8

colorpicker_js = URL(c='static/mColorPicker', f='mColorPicker.min.js')

class ColorPickerWidget(object):
    """
    Colorpicker widget based on  http://code.google.com/p/mcolorpicker/
    """
    def __init__ (self, js = colorpicker_js, button=True, style="", transparency=False):
        import uuid
        uid = str(uuid.uuid4())[:8]
        self._class = "_%s" % uid
        self.style = style
        if transparency == False:
            self.transparency = 'false'
        else:
            self.transparency = 'true'
        if button == True:
            self.data = 'hidden'
            if self.style ==  "":
                self.style = "height:20px;width:20px;"
        else:
            self.data = 'display'
        if not js in response.files:
            response.files.append(js)
    def widget(self, f, v):
        wrapper = DIV()
        inp = SQLFORM.widgets.string.widget(f,v, _value=v, _type='color', _data_text='hidden', _style=self.style, _hex='true', _class=self._class)
        scr = SCRIPT(
        """
        try{
        jQuery.fn.mColorPicker.init.replace = false;
        jQuery.fn.mColorPicker.init.allowTransparency=%s;
        jQuery('input.%s').mColorPicker({'imageFolder': '/%s/static/mColorPicker/'});        
        }
        catch(e){window.alert("Could not run colorpicker. Error: " + String(e));}
        
        """ % (self.transparency, self._class, request.application))
        wrapper.components.append(inp)
        wrapper.components.append(scr)
        return wrapper
color_widget = ColorPickerWidget()


db.define_table('house', 
    Field('color', widget = color_widget.widget))

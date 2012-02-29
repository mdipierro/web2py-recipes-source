# coding: utf8

def JQGRID(table,fieldname=None, fieldvalue=None, col_widths=[],
           colnames=[], _id=None, fields=[],
           col_width=80, width=700, height=300, dbname='db'):    
    # <styles> and <script> section
    response.files.append('http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.9/jquery-ui.js')
    response.files.append('http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.9/themes/ui-darkness/jquery-ui.css')
    for f in ['jqgrid/ui.jqgrid.css',
              'jqgrid/i18n/grid.locale-en.js',
              'jqgrid/jquery.jqGrid.min.js']:
        response.files.append(URL('static',f))
    # end <style> and <script> section
    from gluon.serializers import json
    _id = _id or 'jqgrid_%s' % table._tablename
    if not fields:
        fields = [field.name for field in table if field.readable]
    else:
        fields = fields
    if col_widths:
        if isinstance(col_widths,(list,tuple)):
            col_widths = [str(x) for x in col_widths]
        if width=='auto':
            width=sum([int(x) for x in col_widths])
    elif not col_widths:
        col_widths = [col_width for x in fields]
    colnames = [(table[x].label or x) for x in fields]
    colmodel = [{'name':x,'index':x, 'width':col_widths[i], 'sortable':True} \
                for i,x in enumerate(fields)]
    callback = URL('jqgrid',
               vars=dict(dbname=dbname,
                 tablename=table._tablename,
                 columns=','.join(fields),
                 fieldname=fieldname or '',
                 fieldvalue=fieldvalue,
                 ),
               hmac_key=auth.settings.hmac_key,
               salt=auth.user_id
               )
    script="""                                                                     
jQuery(function(){
   jQuery("#%(id)s").jqGrid({
      url:'%(callback)s',
      datatype: "json",
      colNames: %(colnames)s,
      colModel:%(colmodel)s,
      rowNum:10, rowList:[20,50,100],
      pager: '#%(id)s_pager',
      viewrecords: true,
      height:%(height)s
   });
   jQuery("#%(id)s").jqGrid('navGrid','#%(id)s_pager',{
      search:true,add:false,
      edit:false,del:false
   });
   jQuery("#%(id)s").setGridWidth(%(width)s,false);
   jQuery('select.ui-pg-selbox,input.ui-g-input').css('width','50px');
});
""" % dict(callback=callback,colnames=json(colnames),
           colmodel=json(colmodel),id=_id,
           height=height,width=width)
    return TAG[''](TABLE(_id=_id),
               DIV(_id=_id+"_pager"),
               SCRIPT(script))

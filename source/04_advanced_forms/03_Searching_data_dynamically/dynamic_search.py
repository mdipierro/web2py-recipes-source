# coding: utf8

def build_query(field, op, value):
    if op == 'equals':
        return field == value
    elif op == 'not equal':
        return field != value
    elif op == 'greater than':
        return field > value
    elif op == 'less than':
        return field < value
    elif op == 'starts with':
        return field.startswith(value)
    elif op == 'ends with':
        return field.endswith(value)
    elif op == 'contains':
        return field.contains(value)

def dynamic_search(table):
    tbl = TABLE()
    selected = []
    ops = ['equals','not equal','greater than','less than',
           'starts with','ends with','contains']
    query = table.id > 0
    for field in table.fields:
        chkval = request.vars.get('chk'+field,None)
        txtval = request.vars.get('txt'+field,None)
        opval = request.vars.get('op'+field,None)
        row = TR(TD(INPUT(_type="checkbox",_name="chk"+field,
                          value=chkval=='on')),
                 TD(field),TD(SELECT(ops,_name="op"+field,
                                     value=opval)),
                 TD(INPUT(_type="text",_name="txt"+field,
                          _value=txtval)))
        tbl.append(row)
        if chkval:
            if txtval:
                query &= build_query(table[field],
                                opval,txtval)
            selected.append(table[field])
    form = FORM(tbl,INPUT(_type="submit"))
    results = db(query).select(*selected)
    return form, results

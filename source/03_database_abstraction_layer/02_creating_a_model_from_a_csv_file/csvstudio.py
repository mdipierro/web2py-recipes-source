#!/usr/bin/python
# -*- coding: utf-8 -*-
# license: BSD
# contributors:
# - Massimo Di Pierro <massimo.dipierro@gmail.com>
# - Pierre Mizrahi <pierre.mizrahi@gmail.com>

__all__=['study']

USAGE = """

  csvstudio.py -i input.csv -a

csvstudio.py is a program to analyze and filter data from csv files.

Examples:
- perform a statistical analysis of each column and find dependent cols
  csvstudio.py -a < input.csv
  csvstudio.py -i input.csv -a
- print the first 20 rows that contain the string "2006" and "test"
  csvstudio.py -i input.csv -q "2006 test" -m 20
- add one row containing totals of numerical cells, output to file in csv
  csvstudio.py -i input.csv -q "2006 test" -t -o output.csv
- filter rows where column "name" starts with "test" or Test and column "number" has value < 10
  csvstudio.py -i input.csv -q "name#^[tT]est number<10"
- filter rows where column "name" contains "test" and column "number" has value < 10
  csvstudio.py -i input.csv -q "name#test number<10"
- same as above but compute total, display only 5 rows, show only cols name, number
  csvstudio.py -i input.csv -q "name#test number<10" -t -m 5 -c name,number
- add a column called "compute" with value 2*exp(number)+random()"
  csvstudio.py -i input.csv -r "compute=2*exp(number)+random()"

Important: input must be a csv file. The first row must contain column names.

CHANGELOG:
- can read multiple date formats
- can export web2py models
- can export Django models
"""

def custom_json(o):
    if isinstance(o, (datetime.date,
                      datetime.datetime,
                      datetime.time)):
        return o.isoformat()[:19].replace('T',' ')
    else:
        raise TypeError(repr(o) + " is not JSON serializable")

def guess_type(values):
    import time
    def check(values,f):
        for value in values:
            try:
                if not value is '' and not f(value):
                    return False
            except Exception, e:
                return False
        return True
    if len(values) in (0, len([x for x in values if x==''])):
        return 'string'
    if check(values,lambda v: int(v)==float(v)):
        return 'integer'
    if check(values,lambda v: float(v)):
        return 'double'
    for i in ('%H:%M:%S','%H:%M','%I:%M:%S%p','%I:%M%p'):
        if check(values,lambda v,i=i: time.strptime(v,i)):
            return 'time %s' % i
    for sep in ('/','-'):
        for m in ('%m','%b','%B'):
            for y in ('%y','%Y'):
                for format_order in (['%d', m, y], [y, m, '%d']):
                    i= sep.join(format_order)
                    if check(values,lambda v,i=i: time.strptime(v,i)):
                        return 'date %s' % i
                    for j in ('%H:%M:%S','%H:%M','%I:%M:%S%p','%I:%M%p'):
                        k=i+' '+j
                        if check(values,lambda v,i=k: time.strptime(v,i)):
                            return 'datetime %s' % k
                    i=m+sep+'%d'+sep+y
                    if check(values,lambda v,i=i: time.strptime(v,i)):
                        return 'date %s' % i
                    for j in ('%H:%M:%S','%H:%M','%I:%M:%S%p','%I:%M%p'):
                        k=i+' '+j
                        if check(values,lambda v,i=k: time.strptime(v,i)):
                            return 'datetime %s' % k
    return 'string'

def parse(stream, delimiter=','):
    import csv, re
    regex=re.compile('\W+')

    def clean(data):
        data=data.strip()
        try:
            if str(int(data))==str(data): return int(data)
            return float(data)
        except ValueError:
            return data.strip()
    cols=None
    rows=[]
    for line in csv.reader(stream,delimiter=delimiter):
        if not cols:
            cols=[regex.sub('_',x.strip().lower()) for x in line]
            for i in range(len(cols)):
                while cols[i] in cols[:i]:
                    cols[i] = cols[i]+'2'
        else:
            rows.append(dict((key,clean(line[i] if len(line)>i else '')) for i,key in enumerate(cols)))
    return cols, rows

def run(cols, rows, formulas):
    import math, random
    env={}
    for k in dir(math):
        env[k]=eval('math.'+k)
    for k in dir(random):
        env[k]=eval('random.'+k)
    cols += [item[0] for item in formulas]
    for row in rows:
        for key, f in formulas:
            env.update(row)
            row[key] = eval(f,{},env)
    return cols, rows

def filter(cols, rows, query=''):
    import re
    new_rows = []
    tokens = query.split()
    mem = {}
    def memoize(value):
        try:
            m = mem[value]
        except KeyError:
            m = mem[value] = re.compile(value)
        return m
    def match(k,r):
        if '=' in k:
            key,value=k.split('=',1)
            return str(row[key])==str(value)
        elif '<' in k:
            key,value=k.split('<',1)
            try: return float(row[key])<float(value)
            except ValueError: return False
        elif '<=' in k:
            key,value=k.split('<=',1)
            try: return float(row[key])<=float(value)
            except ValueError: return False
        elif '>' in k:
            key,value=k.split('>',1)
            try: return float(row[key])>float(value)
            except ValueError: return False
        elif '>=' in k:
            key,value=k.split('>=',1)
            try: return float(row[key])>=float(value)
            except ValueError: return False
        elif '#' in k:
            key,value=k.split('#',1)
            return memoize(value).search(str(row[key]))!=None
        else:
            return k in [str(x) for x in row.values()]
    table = []
    table.append(cols)
    sums = dict((h,0.0) for h in cols)
    for k,row in enumerate(rows):
        if sum(match(k,row) and 1 or 0 for k in tokens)==len(tokens):
            table.append([row[h] for h in cols])
            new_rows.append(row)
            for h in cols:
                try:
                    sums[h]+=float(row[h] or 0)
                except TypeError:
                    sums[h]=''
                except ValueError:
                    sums[h]=''
    return new_rows, table, sums

def analysis(cols,rows):
    data = {}
    output = '### Cols\n'
    output += 'cols = %s\n\n' % cols
    equivalence={}
    for h in cols:
        d=data[h]={}
        values = list(set(row[h] for row in rows))
        values.sort()
        for k in cols:
            d['equivalent:'+k]=False
            if k>h:
                values_hk = list(set((row[h],row[k]) for row in rows))
                equivalence[h,k]=(len(values_hk)==len(values) and len(values)>1)
                d['equivalent:'+k]=equivalence[h,k]
        d['values']=values
        d['type']=guess_type(values)
        d['length']=len(values)
        output += '### Column "%s"\n' % h
        output += 'type(value) = "%s"\n' % d['type']
        output += 'len(values) = %i\n' % d['length']
        if len(values)<100:
            output += 'values = %s\n' % values
        else:
            nvalues = [x for x in values if str(x).strip()]
            output += 'min(values) = %s\nmax(values) = %s\n' % (min(nvalues),max(nvalues))
        for k in cols:
            if k>h and equivalence[h,k]:
                output += '%s is equivalent to %s\n' % (h,k)
        output += '\n'
    return output, data

def web2py(name,cols,rows):
    output = 'db.define_table("%s",\n' % name
    equivalence={}
    for h in cols:
        values = list(set(row[h] for row in rows))
        values.sort()
        for k in cols:
            if k>h:
                values_hk = list(set((row[h],row[k]) for row in rows))
                equivalence[h,k]=(len(values_hk)==len(values) and len(values)>1)

        output += '     Field("%s",' % h
        t = guess_type(values)
        if t in ('string','integer','double'):
            output += '"%s"),\n' % t
        elif t.startswith('datetime'):
            output += '"datetime",requires=IS_DATETIME(format="%s")),\n' % t[9:]
        elif t.startswith('time'):
            output += '"time",requires=IS_TIME(format="%s")),\n' % t[5:]
        elif t.startswith('date'):
            output += '"date",requires=IS_DATE(format="%s")),\n' % t[5:]
    output += ')\n'
    return output



def django(name, cols, rows):
    ''' outputs a django model.py content'''
    def _django_fieldname(h):
        ''' returns a django suitable ModelField attribute name'''
        return h.lower().replace(' ', '_')
    def _django_make_boolean_field(field_name, has_blanks):
        if has_blanks:
            return '%s = models.NullBooleanField()\n' % (field_name)
        else:
            return '%s = models.BooleanField()\n' % (field_name)

    output = 'class %s(models.Model):\n' % name
    indent = ' ' * 4 # customizable ?
    for h in cols:
        field_name = _django_fieldname(h)
        values = list(set(row[h] for row in rows))
        has_blanks = any([row[h] == '' for row in rows])
        t = guess_type(values)
        output += indent
        field_options = []
        if has_blanks:
            field_options += ['blank=True', 'null=True']
        if t == 'double':
            output += '%s = models.FloatField(%s)\n' % (field_name, ', '.join(field_options))
        elif t == 'integer':
            # check if we can coerce to a boolean
            if all(v in ('', 0, 1) for v in values):
                output += _django_make_boolean_field(field_name, has_blanks)
            else:
                output += '%s = models.IntegerField(%s)\n' % (field_name, ', '.join(field_options))
        elif t.startswith('datetime'):
            output += '%s = models.DateTimeField(%s)\n' % (field_name, ', '.join(field_options))
        elif t.startswith('time'):
            output += '%s = models.TimeField(%s)\n' % (field_name, ', '.join(field_options))
        elif t.startswith('date'):
            output += '%s = models.DateField(%s)\n' % (field_name, ', '.join(field_options))

        # guessed type is 'string'
        elif all(v.lower() in ['', 'true', 'false'] for v in values):
            # coerce to boolean
            output += _django_make_boolean_field(field_name, has_blanks)
        else:
            if has_blanks:
                # don't allow null = True for CharField or TextField
                field_options = ['blank=True']
            max_length = max(map(len, values))
            min_length = min(map(len, values))
            char_field_length = 0
            if max_length == min_length:
                # guess this is a fixed-length column
                # ...but there is room for a better heuristics...
                char_field_length = max_length
            else:
                # give (hopefully) sufficent space
                char_field_length = max_length * 2
            if char_field_length > 50:
                output += '%s = models.TextField(%s)\n' % (field_name, ', '.join(field_options))
            else:
                field_options.append('max_length=%d' % char_field_length)
                output += '%s = models.CharField(%s)\n' % (field_name, ', '.join(field_options))
    output += '\n\n'
    return output

def study(stream,query='',cols='<all>',formulas=[],delimiter=',',doanalysis=True):
    """

    o = study(input,query='',cols='<all>')

    read a csv file from stream=open('filename','rb') and returns:
    - o['cols'] a list of cols form the csv
    - o['data'] a list of lists containing the cols
    - o['sums'][colname] a sum of values for selected records
    - o['info'][colname]['values'] a list of possible values for colname
    - o['info'][colname]['type'] a guess for the type of col colname
    """
    try: stream.seek(0)
    except IOError: pass
    (cols1, rows) = parse(stream,delimiter)
    if formulas:
        (cols1,rows) = run(cols1,rows,formulas)
    if cols=='<all>': cols = cols1
    rows, data, sums = filter(cols, rows, query)
    output, info = doanalysis and analysis(cols,rows) or ('',{})
    return {'cols':cols, 'data':data, 'sums':sums, 'info':info, 'report':output}


def main():
    import sys, os, optparse
    usage = USAGE
    version= ""
    parser = optparse.OptionParser(usage, None, optparse.Option, version)
    parser.add_option('-i',
                      '--input_filename',
                      default='<stdin>',
                      dest='input_filename',
                      help='the input csv file')
    parser.add_option('-o',
                      '--output_filename',
                      default='',
                      dest='output_filename',
                      help='the output csv file')
    parser.add_option('-q',
                      '--query',
                      default='',
                      dest='query',
                      help='the filter condition')
    parser.add_option('-c',
                      '--columns',
                      default='<all>',
                      dest='cols',
                      help='list of comma separated column names')
    parser.add_option('-a',
                      '--analysis',
                      action='store_true',
                      default=False,
                      dest='analysis',
                      help='perform statistical analysis')
    parser.add_option('-w',
                      '--web2py',
                      default='',
                      dest='web2py',
                      help='spit a web2py model of given name')
    parser.add_option('-D',
                      '--django',
                      default='',
                      dest='django',
                      help='spit a django model of given name')
    parser.add_option('-m',
                      '--max_rows',
                      default='5',
                      dest='max_rows',
                      help='max  number of rows to be displayed')
    parser.add_option('-f',
                      '--format',
                      default='text',
                      dest='format',
                      help='format of the output: text, html, csv, json')
    parser.add_option('-r',
                      '--run',
                      default='',
                      dest='run',
                      help='expressions for computed cols')
    parser.add_option('-d',
                      '--delimiter',
                      default=ord(','),
                      dest='delimiter',
                      help='ascii code of the delimiter (default is comma, i.e. 44)')
    parser.add_option('-t',
                      '--totals',
                      action = 'store_true',
                      default=False,
                      dest='totals',
                      help='compute totals')
    (options, args) = parser.parse_args()
    options.max_rows = int(options.max_rows)

    if not options.input_filename=='<stdin>':
        if not os.path.exists(options.input_filename):
            print 'File %s does not exist' % options.input_filename
            return
        input = open(options.input_filename,'rb')
    else:
        input = sys.stdin
    (cols, rows) = parse(input,delimiter=chr(int(options.delimiter)))
    if options.run:
        formulas = [item.strip().split('=') for item in options.run.split(';')]
        cols,rows = run(cols,rows,formulas)
    cols = options.cols=='<all>' and cols or \
        [x.strip().lower() for x in options.cols.split(',') if x.strip().lower() in cols]
    rows, table, sums = filter(cols, rows, options.query)
    n = len(table)
    if options.totals:
        table.append([sums[h] for h in cols])
    if options.analysis:
        print analysis(cols,rows)[0] # 0 output, 1 dict
    if options.web2py:
        print web2py(options.web2py,cols,rows)
    if options.django:
        print django(options.django, cols, rows)

    output = ''
    if options.format=='text':
        for i in range(min(n,options.max_rows)):
            line = table[i]
            output += '### %i\n' % i
            output += ', '.join('%s=%s' % (h,repr(line[j])) for j,h in enumerate(cols))
            output += '\n'
        if n>options.max_rows and min(n,options.max_rows)>0:
            output += '\n...\n\n'
        if options.totals:
            line = table[n]
            output += '### TOTALS\n'
            output += ', '.join('%s=%s' % (h,repr(line[j])) for j,h in enumerate(cols))
            output += '\n'
    elif options.format=='csv':
        for i,line in enumerate(table):
            output += ','.join(str(x).strip() for x in line)
            output += '\n'
    elif options.format=='json':
        import simplejson
        output = simplejson.dumps(table,default=custom_json)
    elif options.format=='html':
        import cgi
        output += '<table>\n'
        for i,line in enumerate(table):
            if i==0:
                output += '<tr><th>'
                output += '</th><th>'.join(cgi.escape(str(x)) for x in line)
                output += '</th><tr>'
            else:
                output += '<tr><td>'
                output += '</td><td>'.join(cgi.escape(str(x)) for x in line)
                output += '</td><tr>\n'
        output += '<table>\n'
    else:
        output += 'unkown format'
    if options.output_filename:
        open(options.output_filename,'wb').write(output)
    else:
        print output

if __name__=='__main__': main()
 

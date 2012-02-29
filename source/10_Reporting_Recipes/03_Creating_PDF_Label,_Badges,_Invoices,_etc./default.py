# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from uuid import uuid4
from cgi import escape
import os

def get_me_a_pdf():
    title = "This The Doc Title"
    heading = "First Paragraph"
    text = 'bla '* 10000

    styles = getSampleStyleSheet()
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
    doc = SimpleDocTemplate(tmpfilename)
    story = []
    story.append(Paragraph(escape(title),styles["Title"]))
    story.append(Paragraph(escape(heading),styles["Heading2"]))
    story.append(Paragraph(escape(text),styles["Normal"]))
    story.append(Spacer(1,2*inch))
    doc.build(story)
    data = open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    return data

from gluon.contrib.pyfpdf import FPDF
import os

def get_me_a_pyfpdf():
    title = "This The Doc Title"
    heading = "First Paragraph"
    text = 'bla '* 10000

    pdf=FPDF()
    pdf.add_page()
    pdf.set_font('Times','B',15)
    pdf.cell(w=210,h=9,txt=title,border=0,ln=1,align='C',fill=0)
    pdf.set_font('Times','B',15)
    pdf.cell(w=0,h=6,txt=heading,border=0,ln=1,align='L',fill=0)
    pdf.set_font('Times','',12)
    pdf.multi_cell(w=0,h=5,txt=text)
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')

def report():
    response.title = "web2py sample report"
    
    # include a google chart!
    url = "http://chart.apis.google.com/chart?cht=p3&chd=t:60,40&chs=250x100&chl=Hello|World&.png"
    chart = IMG(_src=url, _width="250",_height="100")

    # create a small table with some data:
    rows = [THEAD(TR(TH("Key",_width="70%"), TH("Value",_width="30%"))),
            TBODY(TR(TD("Hello"),TD("60")), 
                  TR(TD("World"),TD("40")))]
    table = TABLE(*rows, _border="0", _align="center", _width="50%")

    if request.extension=="pdf":
        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # create a custom class with the required functionalities 
        class MyFPDF(FPDF, HTMLMixin):
            def header(self): 
                "hook to draw custom page header"
                logo=os.path.join(request.env.web2py_path,"applications",request.application,"private","tutorial","logo_pb.png")
                self.image(logo,10,8,33)
                self.set_font('Arial','B',15)
                self.cell(65) # padding
                self.cell(60,10,response.title,1,0,'C')
                self.ln(20)
                
            def footer(self):
                "hook to draw custom page header (printing page numbers)"
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')
                    
        pdf=MyFPDF()
        # create a page and serialize/render HTML objects
        pdf.add_page()
        pdf.write_html(str(XML(table, sanitize=False)))
        pdf.write_html(str(XML(CENTER(chart), sanitize=False)))
        # prepare PDF to download:
        response.headers['Content-Type']='application/pdf'
        return pdf.output(dest='S')
    else:
        # normal html view:
        return dict(chart=chart, table=table)

def listing():
    response.title = "web2py sample listing"
    
    # define header and footers:
    head = THEAD(TR(TH("Header 1",_width="50%"), 
                    TH("Header 2",_width="30%"),
                    TH("Header 3",_width="20%"), 
                    _bgcolor="#A0A0A0"))
    foot = TFOOT(TR(TH("Footer 1",_width="50%"), 
                    TH("Footer 2",_width="30%"),
                    TH("Footer 3",_width="20%"),
                    _bgcolor="#E0E0E0"))
    
    # create several rows:
    rows = []
    for i in range(1000):
        col = i % 2 and "#F0F0F0" or "#FFFFFF"
        rows.append(TR(TD("Row %s" %i),
                       TD("something", _align="center"),
                       TD("%s" % i, _align="right"),
                       _bgcolor=col)) 

    # make the table object
    body = TBODY(*rows)
    table = TABLE(*[head,foot, body], 
                  _border="1", _align="center", _width="100%")

    if request.extension=="pdf":
        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # define our FPDF class (move to modules if it is reused  frequently)
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                self.set_font('Arial','B',15)
                self.cell(0,10, response.title ,1,0,'C')
                self.ln(20)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')
                    
        pdf=MyFPDF()
        # first page:
        pdf.add_page()
        pdf.write_html(str(XML(table, sanitize=False)))
        response.headers['Content-Type']='application/pdf'
        return pdf.output(dest='S')
    else:
        # normal html view:
        return dict(table=table)
        

def import_csv():
    from gluon.contrib.pyfpdf import Template
    
    f = Template()
    f.parse_csv(infile="/home/reingart/web2py/gluon/contrib/pyfpdf/invoice.csv", delimiter=";", decimal_sep=",")
    for v in f.fields.elements():
        v['align']=  {'I':'L','D':'R','C':'C','':''}.get(v['align'], 'L')
        v['pdf_template_id'] = 1
        db.pdf_element.insert(**v)

def invoice():
    from gluon.contrib.pyfpdf import Template
    import os.path
    
    # generate sample invoice (according Argentina's regulations)

    import random
    from decimal import Decimal

    # read elements from db 
    
    elements = db(db.pdf_element.pdf_template_id==1).select(orderby=db.pdf_element.priority)

    f = Template(format="A4",
             elements = elements,
             title="Sample Invoice", author="Sample Company",
             subject="Sample Customer", keywords="Electronic TAX Invoice")
    
    detail = "Lorem ipsum dolor sit amet, consectetur. " * 5
    items = []
    for i in range(1, 30):
        ds = "Sample product %s" % i
        qty = random.randint(1,10)
        price = round(random.random()*100,3)
        code = "%s%s%02d" % (chr(random.randint(65,90)), chr(random.randint(65,90)),i)
        items.append(dict(code=code, unit='u',
                          qty=qty, price=price, 
                          amount=qty*price,
                          ds="%s: %s" % (i,ds)))

    # divide and count lines
    lines = 0
    li_items = []
    for it in items:
        qty = it['qty']
        code = it['code']
        unit = it['unit']
        for ds in f.split_multicell(it['ds'], 'item_description01'):
            # add item description line (without price nor amount)
            li_items.append(dict(code=code, ds=ds, qty=qty, unit=unit, price=None, amount=None))
            # clean qty and code (show only at first)
            unit = qty = code = None
        # set last item line price and amount
        li_items[-1].update(amount = it['amount'],
                            price = it['price'])

    obs="\n<U>Detail:</U>\n\n" + detail
    for ds in f.split_multicell(obs, 'item_description01'):
        li_items.append(dict(code=code, ds=ds, qty=qty, unit=unit, price=None, amount=None))

    # calculate pages:
    lines = len(li_items)
    max_lines_per_page = 24
    pages = lines / (max_lines_per_page - 1)
    if lines % (max_lines_per_page - 1): pages = pages + 1

    # completo campos y hojas
    for page in range(1, pages+1):
        f.add_page()
        f['page'] = 'Page %s of %s' % (page, pages)
        if pages>1 and page<pages:
            s = 'Continues on page %s' % (page+1)
        else:
            s = ''
        f['item_description%02d' % (max_lines_per_page+1)] = s

        f["company_name"] = "Sample Company"
        f["company_logo"] = os.path.join(request.env.web2py_path,"applications",request.application,"private","tutorial","logo.png")
        f["company_header1"] = "Some Address - somewhere -"
        f["company_header2"] = "http://www.example.com"        
        f["company_footer1"] = "Tax Code ..."
        f["company_footer2"] = "Tax/VAT ID ..."
        f['number'] = '0001-00001234'
        f['issue_date'] = '2010-09-10'
        f['due_date'] = '2099-09-10'
        f['customer_name'] = "Sample Client"
        f['customer_address'] = "Siempreviva 1234"
       
        # print line item...
        li = 0 
        k = 0
        total = Decimal("0.00")
        for it in li_items:
            k = k + 1
            if k > page * (max_lines_per_page - 1):
                break
            if it['amount']:
                total += Decimal("%.6f" % it['amount'])
            if k > (page - 1) * (max_lines_per_page - 1):
                li += 1
                if it['qty'] is not None:
                    f['item_quantity%02d' % li] = it['qty']
                if it['code'] is not None:
                    f['item_code%02d' % li] = it['code']
                if it['unit'] is not None:
                    f['item_unit%02d' % li] = it['unit']
                f['item_description%02d' % li] = it['ds']
                if it['price'] is not None:
                    f['item_price%02d' % li] = "%0.3f" % it['price']
                if it['amount'] is not None:
                    f['item_amount%02d' % li] = "%0.2f" % it['amount']

        if pages == page:
            f['net'] = "%0.2f" % (total/Decimal("1.21"))
            f['vat'] = "%0.2f" % (total*(1-1/Decimal("1.21")))
            f['total_label'] = 'Total:'
        else:
            f['total_label'] = 'SubTotal:'
        f['total'] = "%0.2f" % total

    response.headers['Content-Type']='application/pdf'
    return f.render('invoice.pdf', dest='S')

def index():
    if request.extension == "pdf": response.view = "generic.pdf"
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    response.flash = T('Welcome to web2py')
    return dict(message=T('Hello World'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

# coding: utf8
# intente algo como

response.view = "generic.html"

def index(): return dict(message="hello from badges.py")

import os, os.path
from gluon.contrib.pyfpdf import Template

def create_label():
    pdf_template_id = db.pdf_template.insert(title="sample badge", format="A4")

    # configure optional background image and insert his element
    path_to_image = os.path.join(request.folder, 'static','badge_background.png')
    if path_to_image:
        db.pdf_element.insert(pdf_template_id=pdf_template_id, name='background', type='I', x1=0.0, y1=0.0, x2=85.23, y2=54.75, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='L', text=path_to_image, priority=-1)
    # insert name, company_name, number and attendee type elements:
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='name', type='T', x1=4.0, y1=25.0, x2=62.0, y2=30.0, font='Arial', size=12.0, bold=True,       italic=False, underline=False, foreground=0, background=16777215, align='L', text='', priority=0)
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='company_name', type='T', x1=4.0, y1=30.0, x2=50.0, y2=34.0, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='L', text='', priority=0)
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='no', type='T', x1=4.0, y1=34.0, x2=80.0, y2=38.0, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='R', text='', priority=0)
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='attendee_type', type='T', x1=4.0, y1=38.0, x2=50.0, y2=42.0, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='L', text='', priority=0)
    return dict(pdf_template_id=pdf_template_id)


def copy_labels():
    # read base label/badge elements from db 
    base_pdf_template_id = 2
    elements = db(db.pdf_element.pdf_template_id==base_pdf_template_id).select(orderby=db.pdf_element.priority)
    # setup initial offset and width and height:
    x0, y0 = 10, 10
    dx, dy = 85.5, 55
    # create new template to hold several labels/badges:
    rows, cols = 5,  2
    pdf_template_id = db.pdf_template.insert(title="sample badge %s rows %s cols" % (rows, cols), format="A4")
    # copy the base elements:
    k = 0
    for i in range(rows):
        for j in range(cols):
            k += 1
            for element in elements:
                e = dict(element)
                e['name'] = "%s%02d" % (e['name'], k)
                e['pdf_template_id'] = pdf_template_id
                e['x1'] = e['x1'] + x0 + dx*j
                e['x2'] = e['x2'] + x0 + dx*j
                e['y1'] = e['y1'] + y0 + dy*i
                e['y2'] = e['y2'] + y0 + dy*i
                del e['update_record']
                del e['delete_record']
                del e['id']
                db.pdf_element.insert(**e)
    return {'new_pdf_template_id': pdf_template_id}

def speakers_badges():
    # set template to use from the db:
    pdf_template_id = 3
    
    # query registered users and generate speaker labels
    speakers = db(db.auth_user.id>0).select(orderby=db.auth_user.last_name|db.auth_user.first_name)
    company_name = "web2conf"
    attendee_type = "Speaker"
    
    # read elements from db 
    elements = db(db.pdf_element.pdf_template_id==pdf_template_id).select(orderby=db.pdf_element.priority)

    f = Template(format="A4",
             elements = elements,
             title="Speaker Badges", author="web2conf",
             subject="", keywords="")
    
    # calculate pages:
    label_count = len(speakers)
    max_labels_per_page = 5*2
    pages = label_count / (max_labels_per_page - 1)
    if label_count % (max_labels_per_page - 1): pages = pages + 1

    # fill placeholders for each page
    for page in range(1, pages+1):
        f.add_page()
        k = 0
        li = 0
        for speaker in speakers:
            k = k + 1
            if k > page * (max_labels_per_page ):
                break
            if k > (page - 1) * (max_labels_per_page ):
                li += 1
                #f['item_quantity%02d' % li] = it['qty']
                f['name%02d' % li] = unicode("%s %s" % (speaker.first_name, speaker.last_name), "utf8")
                f['company_name%02d' % li] = unicode("%s %s" % (company_name, ""), "utf8")
                f['attendee_type%02d' % li] = attendee_type
                ##f['no%02d' % li] = li

    response.headers['Content-Type']='application/pdf'
    return f.render('badge.pdf', dest='S')

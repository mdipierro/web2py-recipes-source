# coding: utf8
LANGUAGES = ('en', 'es', 'pt', 'fr', 'hi', 'hu', 'it', 'pl', 'ru')
FLATPAGES_ADMIN = 'you@example.com'
DEFAULT_FLATPAGE_VIEW = "flatpage.html"

db.define_table('flatpage',
    Field('title', notnull=True),
    Field('subtitle', notnull=True),
    Field('c', label='controller'),
    Field('f', label='function'),
    Field('args', label='arguments'),
    Field('view', default=DEFAULT_FLATPAGE_VIEW),
    Field('lang', requires=IS_IN_SET(LANGUAGES), default='en'),
    Field('body', 'text', default=''),
    auth.signature,
)


def flatpage():
    # define languages that don't need translation:
    T.current_languages = ['en', 'en-en']
    
    # select user specified language (via session or browser config)
    if session.lang:
        lang = session.lang
    elif T.accepted_language is not None:
        lang = T.accepted_language[:2]
    else:
        lang = "en"
    T.force(lang)

    title = subtitle = body = ""
    flatpage_id = None
    form = ''
    view = DEFAULT_FLATPAGE_VIEW

    if request.vars and auth.user and auth.user.email==FLATPAGES_ADMIN:
        # create a form to edit the page:
        record = db.flatpage(request.get_vars.id)
        form = SQLFORM(db.flatpage, record)
        if form.accepts(request, session):
            response.flash = T("Page saved")
        elif form.errors:
            response.flash = T("Errors!")
        else:
            response.flash = T("Edit Page")

    if not form:
        # search flatpage according to the current request
        query = db.flatpage.c==request.controller
        query &= db.flatpage.f==request.function
        if request.args:
            query &= db.flatpage.args==request.args(0)
        else:
            query &= (db.flatpage.args==None)|(db.flatpage.args=='')
        query &= db.flatpage.lang==lang
        # execute the query, fetch one record (if any)
        flatpage = db(query).select(orderby=~db.flatpage.created_on, 
        limitby=(0, 1), cache=(cache.ram, 60)).first()        
        if flatpage:
            flatpage_id = flatpage.id
            title = flatpage.title
            subtitle = flatpage.subtitle
            body = flatpage.body
            view = flatpage.view
        else:
            response.flash = T("Page Not Found!")
        if auth.user and auth.user.email==FLATPAGES_ADMIN:
            # if user is authenticated, show edit button:
            form = A(T('edit'), _href=URL(vars=dict(id=flatpage_id)))
                                                    
    # render the page:
    response.title = title
    response.subtitle = subtitle
    response.view = view
    body = XML(body)
    return dict(body=body, form=form)

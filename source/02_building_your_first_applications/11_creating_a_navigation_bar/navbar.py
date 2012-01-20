# coding: utf8

db.define_table('navbar',
    Field("title", "string"),
    Field("url", "string", requires=IS_EMPTY_OR(IS_URL())),
    Field("c", label="Controller"), 
    Field("f", label="Function"), 
    Field("args", label="Arguments"), 
    Field("sortable", "integer"),
    Field("parent_id", "reference navbar"),
    format="%(title)s",
    )

# remove this once app is setup
if not db(db.navbar).count():
    # create default index entry:
    home_id = db.navbar.insert(title="Home", c="default")
    
    # create a "Company" leaf with typical options:
    company_id = db.navbar.insert(title="Company", c="company")
    db.navbar.insert(title="About Us", f='about_us',
                     parent_id=company_id)
    db.navbar.insert(title="Mision & Vision", f='mision_vision',
                     parent_id=company_id)
    db.navbar.insert(title="Our Team", f='our_team',
                     parent_id=company_id)
    
    products_id = db.navbar.insert(title="Products", c="products")
    # Add some "Computers models" to products entry:
    computers_id = db.navbar.insert(title="Computers", f='computers',
                                    parent_id=products_id)
    for model in 'basic', 'pro', 'gamer':
        db.navbar.insert(title="Model %s" % model, args=model, 
                         parent_id=computers_id)

def get_sub_menus(parent_id, default_c=None, default_f=None):
    children = db(db.navbar.parent_id==parent_id)
    for menu_entry in children.select(orderby=db.navbar.sortable):
        # get action or use defaults:
        c = menu_entry.c or default_c
        f = menu_entry.f or default_f 
        # is this entry selected? (current page)
        sel = (request.controller==c and request.function==f and   
          (request.args and request.args==menu_entry.args or True))
        # return each menu item
        yield (T(menu_entry.title), 
         sel, menu_entry.url or URL(c, f, args=menu_entry.args), 
         get_sub_menus(menu_entry.id, c, f)
         )         

response.menu = get_sub_menus(parent_id=None)

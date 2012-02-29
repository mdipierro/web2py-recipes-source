#This is the main function, the one your users go to
def create():
    #Initialize the widget
    add_option = SelectOrAdd(form_title="Add new Product Category",
                             controller="product", 
                             function="add_category",
                             button_text = "Add New")
    #assign widget to field
    db.product.category_id.widget = add_option.widget

    form = SQLFORM(db.product)
    if form.accepts(request, session):
        response.flash = "New product created"
    elif form.errors:
        response.flash = "Please fix errors in form"
    else:
        response.flash = "Please fill in the form"

    #you need jQuery for the widget to work; include here or just put it in your master layout.html
    response.files.append("http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.9/jquery-ui.js")
    response.files.append("http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.9/themes/smoothness/jquery-ui.css")
    return dict(message="Create your product", form = form)

def add_category():
    #this is the controller function that will appear in our dialog
    form = SQLFORM(db.category)

    if form.accepts(request):
        #Successfully added new item
        #do whatever else you may want

        #Then let the user know adding via our widget worked
        response.flash = T("Added")
        target= request.args[0]
        #close the widget's dialog box
        response.js = 'jQuery( "#%s_dialog-form" ).dialog( "close" ); ' %(target)
        #update the options they can select their new category in the main form
        response.js += """jQuery("#%s").append("<option value='%s'>%s</option>");""" \
                % (target, form.vars.id, form.vars.name)
        #and select the one they just added
        response.js += """jQuery("#%s").val("%s");""" % (target, form.vars.id)
        #finally, return a blank form incase for some reason they wanted to add another option
        return form
    elif form.errors:
        # silly user, just send back the form and it'll still be in our dialog box complete with error messages
        return form
    else:
        #hasn't been submitted yet, just give them the fresh blank form
        return form
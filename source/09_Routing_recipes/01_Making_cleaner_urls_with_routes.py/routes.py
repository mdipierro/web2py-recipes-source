# -*- coding: utf-8 -*-

routes_in = (
    # make sure you do not break admin
    ('/admin','/admin'),
    ('/admin/$anything','/admin/$anything'),
    # make sure you do not break appadmin
    ('/$app/appadmin','/$app/appadmin'),
    ('/$app/appadmin/$anything','/$app/appadmin/$anything'),
    # map the specific urls for this the "pages" app
    ('/$username/home','/pages/default/home/$username'),
    ('/$username/css','/pages/default/css/$username'),
    # leave everything else unchanged
)

routes_out = (
    # make sure you do not break admin
    ('/admin','/admin'),
    ('/admin/$anything','/admin/$anything'),
    # make sure you do not break appadmin
    ('/$app/appadmin','/$app/appadmin'),
    ('/$app/appadmin/$anything','/$app/appadmin/$anything'),
    # map the specific urls for this the "pages" app
    ('/pages/default/home/$username','/$username/home'),
    ('/pages/default/css/$username','/$username/css'),
    # leave everything else unchanged
)


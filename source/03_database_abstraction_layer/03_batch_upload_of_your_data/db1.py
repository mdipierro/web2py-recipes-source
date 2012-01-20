# coding: utf8

db.define_table('employees',
    Field('first_name', requires=IS_NOT_EMPTY()),
    Field('last_name', requires=IS_NOT_EMPTY()),
    Field('salary','double', requires=IS_FLOAT_IN_RANGE(0,10**7)))

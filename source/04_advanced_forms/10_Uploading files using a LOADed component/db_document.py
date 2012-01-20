db.define_table('document',
    Field('filename','upload',requires=IS_NOT_EMPTY()),
    Field('uploaded_by',db.auth_user))

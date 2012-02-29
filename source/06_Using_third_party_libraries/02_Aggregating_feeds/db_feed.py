# coding: utf8

db.define_table("feed",
    Field("name"),
    Field("author"),
    Field("email", requires=IS_EMAIL()),
    Field("url", requires=IS_URL(), comment="RSS/Atom feed"),
    Field("link", requires=IS_URL(), comment="Blog href"),
    Field("general", "boolean", comment="Many categories (needs filters)"),
    )

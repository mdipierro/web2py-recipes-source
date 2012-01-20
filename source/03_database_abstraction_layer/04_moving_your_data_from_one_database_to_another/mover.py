#! /usr/env python
# -*- coding: utf-8 -*-

def main():
    other_db = DAL(URI)
    print "URI is %s" % URI
    print 'creating tables...'
    for table in db:
        other_db.define_table(table._tablename,*[field for field in table])
    print 'exporting data...'
    db.export_to_csv_file(open('tmp.sql','wb'))
    print 'importing data...'
    other_db.import_from_csv_file(open('tmp.sql','rb'))
    other_db.commit()
    print other_db
    print 'done!'

if __name__ == "__main__":
    main()


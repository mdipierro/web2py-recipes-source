#! /usr/env python
# -*- coding: utf-8 -*-

for line in open('/tmp/data.txt','r'):
    fullname,salary = line.strip().split('|')
    first_name,last_name = fullname.split(' ')
    r = db.employees.validate_and_insert(
                       first_name=first_name,
                       last_name=last_name,
                       salary=float(salary))
    if r.errors: print line, r.errors

db.commit()

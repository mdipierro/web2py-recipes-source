# -*- coding: utf-8 -*-
def process_reports():
    reports_to_process = db(db.reports.status == 'pending').select()

    # set selected reports to processing so they do not get picked up
    # a second time if the cron process happens to execute again while
    # this one is still executing.
    for report in reports_to_process:
        report.update_record(status='processing')

    db.commit()

    for report in reports_to_process:
        if report.report_type == 'zipcode_breakdown':

            # get all zipcodes
            zipcodes = db(db.clients.zipcode != None).select()

            # if the key does not exist, create it with a value of 0
            zipcode_counts = defaultdict(int)

            for zip in zipcodes:
                zipcode_counts[zip] += 1

            # black box function left up to the developer to implement
            # just assume it returns the filename of the report it created.
            filename = make_pdf_report(zipcode_counts)

            report.update_record(status='done',
                                 completed_on=datetime.datetime.now(),
                                 report_file_loc=filename)

            # commit record so it reflects into the database immediately.
            db.commit()

process_reports()
            
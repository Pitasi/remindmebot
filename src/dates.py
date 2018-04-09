from datetime import datetime
import parsedatetime.parsedatetime as parsedatetime


def parse_date(src_string):
    cal = parsedatetime.Calendar()
    time_struct, status = cal.parse(src_string)
    return datetime(*time_struct[:6])


def now():
    return datetime.now()

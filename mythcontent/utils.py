import iso8601
from django.utils import timezone
import pytz

"""
convenience method to convert a date/time
string from UTC to local
"""
def utc_to_local(dtstr):
    d = iso8601.parse_date(dtstr, 'Etc/UTC')
    if not timezone.is_aware(d):
        d = timezone.make_aware(d, pytz.timezone('Etc/UTC'))
    return timezone.localtime(d)

"""
Given two time/date strings in the format 2015-11-22 18:00:03,
figure out the number of seconds between them.

Pass:
  * Two iso-format time/date strings. We assume that both are UTC.
Return:
  * Difference between them, in seconds (float)
"""
def time_diff_from_strings(start_time, end_time):
    end_dt = iso8601.parse_date(end_time, pytz.timezone('Etc/UTC'))
    start_dt = iso8601.parse_date(start_time, pytz.timezone('Etc/UTC'))
    return end_dt.timestamp() - start_dt.timestamp()

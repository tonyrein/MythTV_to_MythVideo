import iso8601
from django.utils import timezone
import pytz

import paramiko

from nonpublic.settings import SSH_INFOS

"""
Convert a string in iso8601 format representing
a UTC date/time, or a datetime object into a
timezone-aware datetime object.
"""
def iso_to_tz_aware(dtstr):
    if isinstance(dtstr, str):
        d = iso8601.parse_date(dtstr, pytz.timezone('Etc/UTC') )
    else:
        d = dtstr
    if not timezone.is_aware(d):
        d = timezone.make_aware(d, pytz.timezone('Etc/UTC'))
    return d

"""
convenience method to convert a date/time
string from UTC to local
"""
def utc_to_local(dtstr):
    d = iso_to_tz_aware(dtstr)
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
    return (int)(end_dt.timestamp() - start_dt.timestamp())

"""
Execute a 'cp -v...' command on a remote host by means of paramiko.
"""
def copy_file_on_remote_host(hostname, source_filespec, destination_dir):
    sshinf = SSH_INFOS[hostname]
    user = sshinf['user']
    pword = sshinf['password']
    port = sshinf.get('port', 22)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname, username=user,password=pword,port=port,
        allow_agent=False, look_for_keys=False
        )
    mkdir_cmd = 'mkdir -p {}'.format(destination_dir)
    copy_cmd = 'cp -v {} {}'.format(source_filespec, destination_dir)
    stdin,stdout,stderr=ssh_client.exec_command(mkdir_cmd)
    stdout.readlines()
    stdin,stdout,stderr=ssh_client.exec_command(copy_cmd)
    stdout.readlines()


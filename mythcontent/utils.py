import iso8601
from django.utils import timezone
import pytz
import paramiko

from nonpublic.settings import SSH_INFOS

"""
Convert a string in iso8601 format representing
a UTC date/time, or a datetime object into a
timezone-aware datetime object.

Pass:
  * dtstr -- either a datetime object or a string
    (in iso8601 format) representing a date and time.
Return:
  A timezone-aware datetime.
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
Pass: a datetime, possibly not tz-aware
Return: a timezone-aware datetime,
using UTC.
"""
def ensure_tz_aware(dt):
    if not timezone.is_aware(dt):
        dt = timezone.make_aware(dt, pytz.timezone('Etc/UTC'))
    return dt

"""
Pass: a timezone-aware datetime in
any arbitrary timezone

Return: a timezone-aware datetime using UTC
"""
def ensure_utc(dt):
    if not 'UTC' in dt.tzinfo._tzname.upper():
        dt = dt.astimezone(pytz.timezone('Etc/UTC'))
    return dt

"""
Pass: a tz-aware datetime in utc
Return: the equivalent local dt
From http://stackoverflow.com/questions/4563272/how-to-convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-stand/13287083#13287083
"""
def utc_dt_to_local_dt(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
    
"""
Given two time/date strings in the format 2015-11-22 18:00:03,
figure out the number of seconds between them.

Pass:
  * Two iso-format time/date strings. We assume that both are UTC.
Return:
  * Difference between them, in seconds (int)
"""
def time_diff_from_strings(start_time, end_time):
    end_dt = iso8601.parse_date(end_time, pytz.timezone('Etc/UTC'))
    start_dt = iso8601.parse_date(start_time, pytz.timezone('Etc/UTC'))
    return (int)(end_dt.timestamp() - start_dt.timestamp())

def make_ssh_client(hostname):
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
    return ssh_client

"""
Execute a 'cp -v...' command on a remote host by means of paramiko.
"""
def copy_file_on_remote_host(hostname, source_filespec, destination_dir):
    mkdir_cmd = 'mkdir -p {}'.format(destination_dir)
    copy_cmd = 'cp -v {} {}'.format(source_filespec, destination_dir)
    cl=make_ssh_client(hostname)
    stdin,stdout,stderr=cl.exec_command(mkdir_cmd)
    stdout.readlines()
    stdin,stdout,stderr=cl.exec_command(copy_cmd)
    stdout.readlines()

"""
Given a remote host and directory on that host,
return a list. Each element of the list is
a (file type, filename, filesize) tuple.
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
    stat_cmd='stat -c "%F*%n*%s" {}'.format(dirname)
    stdin,stdout,stderr=ssh_client.exec_command(stat_cmd)
    ret_list=[]
    for line in stdout.readlines():
        ret_list.append( ( line.strip().split('*') ) )
    return ret_list


Works by executing the command 'stat -c "%F*%n*%s" dirname/*'
on the remote host.
"""
def list_files_on_remote_host(hostname, spec):
    stat_cmd='stat -c "%F*%n*%s" {}'.format(spec)
    cl=make_ssh_client(hostname)
    stdin,stdout,stderr=cl.exec_command(stat_cmd)
    ret_list=[]
    for line in stdout.readlines():
        ret_list.append( ( line.strip().split('*') ) )
    return ret_list
    

    

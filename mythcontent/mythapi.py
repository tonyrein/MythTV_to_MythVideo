import urllib.request
import xmltodict
import iso8601
from django.utils import timezone
import pytz

# from .dto import storage_group, tv_recording, myth_video


from collections import namedtuple

# Streamable structures to hold info about items manipulated
# via Myth API calls:
storage_group = namedtuple('StorageDir', ['host','name','directory'])

tv_recording = namedtuple('TVRecording', ['title', 'subtitle', 'description', 'start_at', 'duration', 'channel_number', 'host',
    'storage_group', 'file_name', 'file_size', 'channel_id', 'start_ts' ])

myth_video = namedtuple(
                    'MythVideo',
                     ['title','subtitle','description','length','play_count','season','episode','watched','content_type','file_name','host',]
                     )


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
convenience method to convert a datetime from
local to UTC
For now, assume dt is timezone-aware -- otherwise
we wouldn't know what timezone we're converting from.
"""
def local_to_utc(dt):
    return timezone.localtime(dt, pytz.timezone('Etc/UTC'))
    
from collections import namedtuple

storage_group = namedtuple('StorageDir', ['host','name','directory'])

tv_recording = namedtuple('TVRecording', ['title', 'subtitle', 'description', 'start_at', 'duration', 'channel_number', 'host',
    'storage_group', 'file_name', 'file_size', 'channel_id', 'start_ts' ])

myth_video = namedtuple(
                    'MythVideo',
                     ['title','subtitle','description','length','play_count','season','episode','watched','content_type','file_name','host',]
                     )

class MythApi(object):
    """
    This class encapsulates the code to interact with a
    MythTV server via its API.
    It is a singleton.
    """
    __instance = None
    
    def __new__(cls, server_name='mythbackend1', server_port=6544):
        if MythApi.__instance is None:
            MythApi.__instance = object.__new__(cls)
            MythApi.__instance.server_name = server_name
            MythApi.__instance.server_port = server_port
            MythApi.__instance.storage_groups = MythApi.__instance._get_myth_storage_group_list()
            MythApi.__instance.video_storage_group = MythApi.__instance.get_storage_dir(name='Videos')
            MythApi.__instance.default_storage_group = MythApi.__instance.get_storage_dir(name='Default')
        return MythApi.__instance
            
    
#     def __init__(self, server_name = 'mythbackend1', port=6544):
#         self.server_name = server_name
#         self.server_port = port
#         self.storage_groups = self._get_myth_storage_group_list()
#         self.video_storage_group = self.get_storage_dir(name='Videos')
#         self.default_storage_group = self.get_storage_dir(name='Default')

    """
    Make a call to the MythTV API and request XML back from MythTV server.
    Pass:
      * name of API service
      * name of API call within service
      * data (optional)
      * headers (optional)
    Returns:
      * An ordereddict created by parsing the XML returned from the MythTV server
    """
    def _call_myth_api_for_xml(self,service_name, call_name, data=None, headers=None):
        # urlopen doesn't always work if headers is None:
        if headers is None:
            headers = {}
        # Does headers contain 'Accept'?
        if 'Accept' in headers:
            # If headers['Accept'] is requesting JSON, delete that key.
            if headers['Accept'] == 'text/javascript' or headers['Accept'] == 'application/json':
                del headers['Accept']
        # Assemble url:
        url = (
            "http://{}:{}/{}/{}".format(self.server_name, self.server_port, service_name, call_name)
            )
        # Make a Request object and pass it to the server.
        # Use the returned result to make some XML to return to our caller
        req = urllib.request.Request(url, data, headers)
        with urllib.request.urlopen(req) as response:
            the_answer = response.read()
            return xmltodict.parse(the_answer)
        

    """
    Gets list of storage groups available to
    MythTV server self.server_name.
     Pass: self
     Return: list, each element of which is
     a (host, name, directory) namedtuple.
     On failure, or if there are no storage groups, returns empty list.
    """
    def _get_myth_storage_group_list(self):
        sgxml = self._call_myth_api_for_xml('Myth', 'GetStorageGroupDirs')
        sgdirs = sgxml['StorageGroupDirList']['StorageGroupDirs']['StorageGroupDir']
        retlist = []
        for sg in sgdirs:
            retlist.append(storage_group(sg['HostName'],sg['GroupName'],sg['DirName']))
        return retlist


    """
    Pass:
     * storage group name
     * host (optional)
     (If no host is given, assume self.server_name.)
    Return:
     * the corresponding directory, or None if no match
    """
    def get_storage_dir(self, name='', host=None):
        if host is None:
            host = self.server_name
        for sg in self.storage_groups:
            if sg.host == host and sg.name == name:
                return sg.directory
        return None

    """
    Calls the Myth server and gets a list
    of recorded TV programs. Does not return
    all the info returned by the API call, only
    that which we'll need:
    'title', 'subtitle', 'start_at', 'length', 'channel_id', 'host',
    'storage_group', 'file_name', 'file_size'
    Pass: self
    Return: list, each element of which is a named
    tuple with above members
    If api call fails, return None.
    If program list is empty, return []
    """
    def get_myth_tv_program_list(self):
        prog_dict = self._call_myth_api_for_xml('Dvr', 'GetRecordedList')
        prog_list = prog_dict['ProgramList']['Programs']['Program']
        retlist = []
        for p in prog_list:
            # Get duration:
            start_date_local = utc_to_local(p['Recording']['StartTs'])
            end_date_local = utc_to_local(p['Recording']['EndTs'])
            prog_dur = end_date_local - start_date_local
            # Break duration into components:
            seconds = prog_dur.seconds
            days, seconds = divmod(seconds, 86400)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            # Construct a string to represent the duration:
            if days > 0:
                dur_str = '%d day' % (days)
                if days > 1:
                    dur_str = dur_str + 's'
                dur_str = dur_str + ' '
            else:
                dur_str = ''
            dur_str = dur_str + '%dh %02dm' % (hours, minutes)
            start_at_string = start_date_local.strftime("%m/%d/%Y, %I:%M %p")
            # Make a tv_recording namedtuple and store it in the list to be returned:
            retlist.append( tv_recording(p['Title'], p['SubTitle'], p['Description'],
							 start_at_string, dur_str, p['Channel']['ChanNum'], p['HostName'],
                            p['Recording']['StorageGroup'], p['FileName'], p['FileSize'],
                            p['Channel']['ChanId'], p['Recording']['StartTs'] ) )
        return retlist
        
    def get_mythvideo_list(self):
        video_dict = self._call_myth_api_for_xml('Video', 'GetVideoList')
        video_list = video_dict['VideoMetadataInfoList']['VideoMetadataInfos']['VideoMetadataInfo']
        retlist = []
        for v in video_list:
            retlist.append(
                        myth_video(v['Title'], v['SubTitle'], v['Description'], v['Length'], v['PlayCount'], v['Season'],
                                v['Episode'], v['Watched'], v['ContentType'], v['FileName'], v['HostName'] )
                        )
        return retlist
    
    """
    Ask the Myth API for a single TV program, identified by channel and
    start time. Note that this uses the channel id and not the channel
    number, and the "StartTS" time (the time the recording actually started,
    as opposed to the time the program was scheduled to begin).
    """
    # Might not be needed. Don't define it yet.
#     def get_myth_tv_program(self, channel_id, start_ts):
#     	data = { 'ChanId': channel_id, 'StartTime': start_ts }
#     	prog_dict = self._call_myth_api_for_xml('Dvr', 'GetRecorded', data)
#             

    

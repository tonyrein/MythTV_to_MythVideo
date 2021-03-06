'''
Created on Nov 22, 2015

@author: tony

This class is a wrapper to encapsulate
a server host:port and the code to make
an api call to that server.

In addition, it keeps track of MythTV "storage groups."
Storage groups are constructs used to keep track of where
media files on a MythTV system are stored. Each storage group
has an id (which we ignore), a name, a host, and a directory.

This class's __init__ makes a MythTV API call to get the list
of storage groups; in order to avoid doing this over and over,
this class is a singleton.

'''
from collections import OrderedDict
import json
import urllib.request
# import xmltodict

from django.conf import settings

class MythApi(object):
    __instance = None
    def __new__(cls, server_name=settings.API_SERVER, server_port=settings.API_PORT):
        if MythApi.__instance is None:
            MythApi.__instance = object.__new__(cls)
            MythApi.__instance.server_name = server_name
            MythApi.__instance.server_port = server_port
            MythApi.__instance._storage_groups = MythApi.__instance._fill_myth_storage_group_list()
            MythApi.__instance.default_directory = MythApi.__instance.storage_dir_for_name('Default', server_name)
        return MythApi.__instance
    """
    Make a call to the MythTV API and request JSON back from MythTV server.
    Pass:
      * name of API service
      * name of API call within service
      * data (optional) - a dict of parameters for the call
      * headers (optional)
    Returns:
      * A JSON object built from the data returned from the MythTV server
    Raises:
      * HTTPError
    """
    def _call_myth_api(self,service_name, call_name, data=None, headers=None):
        # urlopen doesn't always work if headers is None:
        if headers is None:
            headers = {}
        # Tell server to send back JSON:
        headers['Accept'] = 'application/json'
        
        if data:
            DATA=urllib.parse.urlencode(data)
            DATA=DATA.encode('utf-8')
        else:
            DATA=None
        
        # Assemble url:
        url = (
            "http://{}:{}/{}/{}".format(self.server_name, self.server_port, service_name, call_name)
            )
        # Make a Request object and pass it to the server.
        # Use the returned result to make some XML to return to our caller
        req = urllib.request.Request(url, data=DATA, headers=headers)
        if DATA:
            req.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
        try:
            with urllib.request.urlopen(req) as response:
                the_answer = response.read()
                if the_answer:
                    the_answer = the_answer.decode('utf-8')
                    return json.loads(the_answer)
        except Exception as e:
            return { 'Exception': e.__repr__() }
#             return d
#             return json.loads("{'Exception':" + e.__repr__() + "}")
        
        
    """
    Gets list of storage groups available to
    MythTV server self.server_name.
     Pass: self
     Return: list, each element of which is an ordereddict with the following keys:
       Id,  GroupName,  HostName,  DirName
    """
    def _fill_myth_storage_group_list(self):
        j = self._call_myth_api('Myth', 'GetStorageGroupDirs')
        return j['StorageGroupDirList']['StorageGroupDirs']
    
    """
    storage_groups() is a property because
         it's read-only.
    """
    @property
    def storage_groups(self):
        return self._storage_groups    
    
    """
    Pass: Storage group name and host name
    Return: Disk directory, or None if no match.
    
    """
    def storage_dir_for_name(self, group_name, hostname=None):
        if hostname is None:
            hostname = self.server_name
        for g in self.storage_groups:
            if g['GroupName'] == group_name and g['HostName'] == hostname:
                return g['DirName']
        return None 

class ChannelApi(object):
    __instance = None # class attribute
    __api_service_name = 'Channel'
    def __new__(cls):
        if ChannelApi.__instance is None:
            ChannelApi.__instance = object.__new__(cls)
            ChannelApi.__instance.api = MythApi()
            ChannelApi.__instance.server_name = ChannelApi.__instance.api.server_name 
        return ChannelApi.__instance
    """
    Pass: Channel id, for example '1008'
    Returns: an ordered dict with the following keys:
    ['@xmlns:xsi', '@version', '@serializerVersion', 'ChanId', 'ChanNum', 'CallSign',
     'IconURL', 'ChannelName', 'MplexId', 'TransportId', 'ServiceId', 'NetworkId',
      'ATSCMajorChan', 'ATSCMinorChan', 'Format', 'Modulation', 'Frequency', 'FrequencyId',
       'FrequencyTable', 'FineTune', 'SIStandard', 'ChanFilters', 'SourceId', 'InputId',
        'CommFree', 'UseEIT', 'Visible', 'XMLTVID', 'DefaultAuth', 'Programs']
    This assumes that a valid channel id is passed. If the channel id is invalid, the
    api call will return an exception code.
    """
    def get_channel_info(self,channel_id):
        res_dict = self.api._call_myth_api(ChannelApi.__api_service_name, 'GetChannelInfo',
                 { 'ChanID': channel_id } )
        if 'Exception' in res_dict:
            raise Exception("Problem getting channel info for channel {}: {}".format(channel_id, res_dict['Exception']))
        else:
            return res_dict['ChannelInfo']
        
        
class TvRecordingApi(object):
    __instance = None # class attribute
    __api_service_name = 'Dvr'
    def __new__(cls):
        if TvRecordingApi.__instance is None:
            TvRecordingApi.__instance = object.__new__(cls)
            TvRecordingApi.__instance.api = MythApi()
            TvRecordingApi.__instance._tv_recordings = None
        return TvRecordingApi.__instance
    
    """
    Queries the MythAPI server for a list of the tv recordings.
    Pass: nothing
    Return: a list, each element of which is an ordereddict with the following keys:
       StartTime, EndTime, Title, SubTitle, Category, CatType, Repeat, VideoProps,
       AudioProps, SubProps, SeriesId, ProgramId, Stars, FileSize, LastModified, ProgramFlags,
       FileName, HostName, Airdate, Description, Inetref, Season, Episode, Channel,
       Recording, Artwork,
       FileSpec, Duration
       Note that the values for several of these keys (Channel, Recording, Artwork) are
       ordereddicts in turn.
       For Channel, the keys are:
           ChanId,  ChanNum,  CallSign,  IconURL,  ChannelName,  MplexId,  TransportId,  ServiceId,
            NetworkId,  ATSCMajorChan,  ATSCMinorChan,  Format,  Modulation,  Frequency,  FrequencyId,
             FrequencyTable,  FineTune,  SIStandard,  ChanFilters,  SourceId,  InputId,  CommFree,
              UseEIT,  Visible,  XMLTVID,  DefaultAuth,  Programs
      For Recording, the keys are:
        Status,  Priority,  StartTs,  EndTs,  RecordId,  RecGroup,  PlayGroup,  StorageGroup,  RecType,  DupInType,  DupMethod,  EncoderId,  Profile
      For Artwork, the one key is:
        ArtworkInfos
        
      The 'FileSpec' and 'Duration' keys/values are calculated by this method and added on to
      the value returned by the Myth API call.
      
      The 'StartTs' and 'EndTs' fields are used to calculate the duration -- these represent the
      actual start and end times of the recording; the fields 'StartTime' and 'EndTime' are the
      scheduled times, and do not reflect the fact that the recording may have started and/or
      ended at other than the scheduled times.
      
    """
    def get_mythtv_recording_list(self):
        res_dict = self.api._call_myth_api(TvRecordingApi.__api_service_name, 'GetRecordedList')
        if 'Exception' in res_dict:
            raise Exception("Problem getting MythTV recording list: {}".format(res_dict['Exception']))
        else:
            return res_dict['ProgramList']['Programs']
    """
    Call MythTV api to remove this recording. If successful,
    remove the recording from our internal list.
    
    Pass:
      * JSON object: the program to delete
      (an element of self._tv_recordings) 
    Return:
      * True if call succeeds, False if it fails
      (no such recording, for example)
      
      Note that if the recording has already been marked
      as deleted in MythTV, this method will still return
      True. This might occur if there has been a previous
      call to this method, causing MythTV to mark the recording
      as deleted, but MythTV has not yet done the actual
      erasure.
 
    """
    def erase(self, recording):
        DATA = {'ChanId': recording.channel.channel_id, 'StartTime': recording.start_at }
        res_dict = self.api._call_myth_api(TvRecordingApi.__api_service_name, 'RemoveRecorded',
                                data=DATA)
        if 'Exception' in res_dict:
            raise Exception("Problem erasing MythTV recording: {}".format(res_dict['Exception']) )
        else:
            return 'bool' in res_dict and res_dict['bool'] == 'true'

class VideoApi(object):
    __instance = None # class attribute
    __api_service_name = 'Video'
    def __new__(cls):
        if VideoApi.__instance is None:
            VideoApi.__instance = object.__new__(cls)
            VideoApi.__instance.api = MythApi()
            VideoApi.__instance._videos = None
            VideoApi.__instance.video_directory = VideoApi.__instance.api.storage_dir_for_name('Videos')
            VideoApi.__instance.server_name = VideoApi.__instance.api.server_name 
        return VideoApi.__instance
    
    def add_to_mythvideo(self, filename, hostname=None):
        if hostname is None:
            hostname = self.server_name
        res_dict = self.api._call_myth_api(VideoApi.__api_service_name, 'AddVideo',
                 { 'FileName': filename, 'HostName': hostname} )
        if 'Exception' in res_dict:
            raise Exception("Problem adding MythVideo file {}: {}".format(filename, res_dict['Exception']) )
        else:
            return 'bool' in res_dict and res_dict['bool'] == 'true'
        
    def find_in_mythvideo(self, filename, hostname=None):
        if hostname is None:
            hostname = self.server_name
        res_dict = self.api._call_myth_api(VideoApi.__api_service_name, 'GetVideoByFileName',
                 { 'FileName': filename } )
        if 'Exception' in res_dict:
            if res_dict['Exception'].getcode() == 500:
                # probably just no such file
                return None
            else:
                raise Exception("Problem finding MythVideo file {}: {}".format(filename, res_dict['Exception']) )
        else:
            return res_dict['VideoMetadataInfo']

    """
    Queries the MythAPI server for a list of the contents of MythVideo.
    Pass: nothing
    Return: a list, each element of which is a JSON object with the following keys:
         Id, Title, SubTitle, Tagline, Director, Studio, Description, Certification, Inetref, Collectionref,
          HomePage, ReleaseDate, AddDate, UserRating, Length, PlayCount, Season, Episode, ParentalLevel,
           Visible, Watched, Processed, ContentType, FileName, Hash, HostName, Coverart, Fanart, Banner,
             Screenshot,  Trailer,  Artwork
        Further, if el is one of the elements, then el['Artwork']['ArtworkInfos']['ArtworkInfo'] is
        a JSON object with the keys:
            URL,  FileName,  StorageGroup,  Type
    """
    def __fill_myth_video_list(self):
        video_dict = self.api._call_myth_api(VideoApi.__api_service_name, 'GetVideoList')
        return video_dict['VideoMetadataInfoList']['VideoMetadataInfos']
    
    @property
    def videos(self):
        if self._videos is None:
            self._videos = self.__fill_myth_video_list()
        return self._videos

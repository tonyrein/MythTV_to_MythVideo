import urllib.request
import xmltodict
from django.db import models
from django.conf import settings
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
class MythApi(object):
    __instance = None
    def __new__(cls, server_name=settings.API_SERVER, server_port=settings.API_PORT):
        if MythApi.__instance is None:
            MythApi.__instance = object.__new__(cls)
            MythApi.__instance.server_name = server_name
            MythApi.__instance.server_port = server_port
            MythApi.__instance._storage_groups = MythApi.__instance._fill_myth_storage_group_list()
        return MythApi.__instance
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
    def _call_myth_api(self,service_name, call_name, data=None, headers=None):
        # urlopen doesn't always work if headers is None:
        if headers is None:
            headers = {}
        # Does headers contain 'Accept'? If so, make sure it's not asking for JSON.
        if 'Accept' in headers:
            if headers['Accept'] in [ 'text/javascript', 'application/json' ]:
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
     Return: list, each element of which is an ordereddict with the following keys:
       Id,  GroupName,  HostName,  DirName
    """
    def _fill_myth_storage_group_list(self):
        sgxml = self._call_myth_api('Myth', 'GetStorageGroupDirs')
        return sgxml['StorageGroupDirList']['StorageGroupDirs']['StorageGroupDir']
    
    """
    storage_groups() is a property because it's read-only.
    """
    @property
    def storage_groups(self):
        return self._storage_groups    
    
    """
    Pass:
        * Storage group name
        * (Optional) host name
        If host name is None, use settings.API_SERVER
    Return: Disk directory, or None if no match.
    
    Assumes: host is same as self.server_name
    """
    def storage_dir_for_name(self, group_name, hostname=settings.API_SERVER):
        for g in self.storage_groups:
            if g[1] == group_name and g[2] == hostname:
                return g[3]
        return None         

class VideoApi(object):
    __instance = None # class attribute
    __api_service_name = 'Video'
    def __new__(cls):
        if VideoApi.__instance is None:
            VideoApi.__instance = object.__new__(cls)
            VideoApi.__instance.api = MythApi()
            VideoApi.__instance._videos = None 
        return VideoApi.__instance
    
    

    """
    Queries the MythAPI server for a list of the contents of MythVideo.
    Pass: nothing
    Return: a list, each element of which is an ordereddict with the following keys:
         Id, Title, SubTitle, Tagline, Director, Studio, Description, Certification, Inetref, Collectionref,
          HomePage, ReleaseDate, AddDate, UserRating, Length, PlayCount, Season, Episode, ParentalLevel,
           Visible, Watched, Processed, ContentType, FileName, Hash, HostName, Coverart, Fanart, Banner,
             Screenshot,  Trailer,  Artwork
        Further, if el is one of the elements, then el['Artwork']['ArtworkInfos']['ArtworkInfo'] is
        an ordered dict with the keys:
            URL,  FileName,  StorageGroup,  Type
         
    """
    def __fill_myth_video_list(self):
        video_dict = self.api._call_myth_api(VideoApi.__api_service_name, 'GetVideoList')
        return video_dict['VideoMetadataInfoList']['VideoMetadataInfos']['VideoMetadataInfo']
    
    @property
    def videos(self):
        if self._videos is None:
            self._videos = self.__fill_myth_video_list()
        return self._videos
    

class TvRecordingApi(object):
    __instance = None # class attribute
    __api_service_name = 'Dvr'
    def __new__(cls, server_name='mythbackend1', server_port=6544):
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
       Recording, Artwork
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
    """
    def __fill_myth_tv_recording_list(self):
        prog_dict = self._call_myth_api(TvRecordingApi.__api_service_name, 'GetRecordedList')
        return prog_dict['ProgramList']['Programs']['Program']
        
    @property
    def tv_recordings(self):
        if self._tv_recordings is None:
            self._tv_recordings = self.__fill_myth_tv_recording_list()
        return self._tv_recordings
        
# class StorageGroupApi(object):
#     __instance = None # class attribute
#     __api_service_name = 'Myth'
#     def __new__(cls, server_name='mythbackend1', server_port=6544):
#         if StorageGroupApi.__instance is None:
#             StorageGroupApi.__instance = object.__new__(cls)
#             StorageGroupApi.__instance.api = MythApi(server_name, server_port)
#             StorageGroupApi.__instance._storage_groups = None
#         return StorageGroupApi.__instance
# #     """
# #     Gets list of storage groups available to
# #     MythTV server self.server_name.
# #      Pass: self
# #      Return: list, each element of which is an ordereddict with the following keys:
# #        Id,  GroupName,  HostName,  DirName
# #     """
# #     def _fill_myth_storage_group_list(self):
# #         sgxml = self.api._call_myth_api(StorageGroupApi.__api_service_name, 'GetStorageGroupDirs')
# #         return sgxml['StorageGroupDirList']['StorageGroupDirs']['StorageGroupDir']
# #     
#     @property
#     def storage_groups(self):
#         if self._storage_groups is None:
#             self._storage_groups = self._fill_myth_storage_group_list()
#         return self._storage_groups
#     
"""
VideoDao is a Django ORM model class
"""
    
class VideoDao(models.Model):
    intid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    subtitle = models.TextField()
    tagline = models.CharField(max_length=255, blank=True, null=True)
    director = models.CharField(max_length=128)
    studio = models.CharField(max_length=128, blank=True, null=True)
    plot = models.TextField(blank=True, null=True)
    rating = models.CharField(max_length=128)
    inetref = models.CharField(max_length=255)
    collectionref = models.IntegerField()
    homepage = models.TextField()
    year = models.IntegerField()
    releasedate = models.DateField()
    userrating = models.FloatField()
    length = models.IntegerField()
    playcount = models.IntegerField()
    season = models.SmallIntegerField()
    episode = models.SmallIntegerField()
    showlevel = models.IntegerField()
    filename = models.TextField()
    hash = models.CharField(max_length=128)
    coverfile = models.TextField()
    childid = models.IntegerField()
    browse = models.IntegerField()
    watched = models.IntegerField()
    processed = models.IntegerField()
    playcommand = models.CharField(max_length=255, blank=True, null=True)
    category = models.IntegerField()
    trailer = models.TextField(blank=True, null=True)
    host = models.TextField()
    screenshot = models.TextField(blank=True, null=True)
    banner = models.TextField(blank=True, null=True)
    fanart = models.TextField(blank=True, null=True)
    insertdate = models.DateTimeField(blank=True, null=True)
    contenttype = models.CharField(max_length=43)

    class Meta:
        managed = False
        db_table = 'videometadata'
        
    @classmethod
    def create(cls, filename=None):
        v = cls(filename)
        #############################################
        # If filename is not None, then call the    #
        # API Video/GetVideoByFileName call.        #
        # If the API call fails, throw an exception.#
        # If MythTV API Video/GetVideoByFileName    #
        # returns success with this filename,       #
        # find corresponding record in DB and       #
        # set our values from that record.          #
        # If failure, throw an exception            #
        #                                           #
        # If filename is not None, but the          #
        # GetVideoByFileName call returns "not      #
        # found," then:                             #
        #   1. copy filename to the Videos SG, if   #
        #       needed                              #
        #   2. call Video/AddVideo                  #
        #   3. Get the row from db, set our values. #
        #############################################
        return v
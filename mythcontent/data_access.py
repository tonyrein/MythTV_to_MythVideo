import urllib.request
import xmltodict

'''
Created on Nov 22, 2015

@author: tony

This class is just a wrapper to encapsulate
a server host:port and the code to make
an api call to that server.
'''
class MythApi(object):
    def __init__(self, server_name='mythbackend1', server_port=6544):
        self.server_name = server_name
        self.server_port = server_port
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
            

class VidApi(object):
    __instance = None # class attribute
    __api_service_name = 'Video'
    def __new__(cls, server_name='mythbackend1', server_port=6544):
        if VidApi.__instance is None:
            VidApi.__instance = object.__new__(cls)
            VidApi.__instance.api = MythApi(server_name, server_port)
            VidApi.__instance._videos = None 
        return VidApi.__instance
    
    

    """
    Queries the MythAPI server for a list of the contents of MythVideo.
    Pass: nothing
    Return: a list, each element of which is an ordereddict with the following keys:
         Id, Title, SubTitle, Tagline, Director, Studio, Description, Certification, Inetref, Collectionref,
          HomePage, ReleaseDate, AddDate, UserRating, Length, PlayCount, Season, Episode, ParentalLevel,
           Visible, Watched, Processed, ContentType, FileName, Hash, HostName, Coverart, Fanart, Banner,
    """
    def __fill_myth_video_list(self):
        video_dict = self.api._call_myth_api(VidApi.__api_service_name, 'GetVideoList')
        return video_dict['VideoMetadataInfoList']['VideoMetadataInfos']['VideoMetadataInfo']
    
    @property
    def videos(self):
        if self._videos is None:
            self._videos = self.__fill_myth_video_list()
        return self._videos
    

class TvRecordingApi(object):
    __instance = None # class attribute
    def __new__(cls, server_name='mythbackend1', server_port=6544):
        if TvRecordingApi.__instance is None:
            TvRecordingApi.__instance = object.__new__(cls)
            TvRecordingApi.__instance.api = MythApi(server_name, server_port)
            TvRecordingApi.__instance.storage_groups = TvRecordingApi.__instance._get_myth_tvrecording_list()
        return TvRecordingApi.__instance
    
    

class StorageGroupApi(object):
    __instance = None # class attribute
    def __new__(cls, server_name='mythbackend1', server_port=6544):
        if StorageGroupApi.__instance is None:
            StorageGroupApi.__instance = object.__new__(cls)
            StorageGroupApi.__instance.api = MythApi(server_name, server_port)
            StorageGroupApi.__instance.storage_groups = StorageGroupApi.__instance._get_myth_storage_group_list()
        return StorageGroupApi.__instance
    """
    Gets list of storage groups available to
    MythTV server self.server_name.
     Pass: self
     Return: list, each element of which is
     a (host, name, directory) namedtuple.
     On failure, or if there are no storage groups, returns empty list.
    """
    def _get_myth_storage_group_list(self):
        sgxml = self.api._call_myth_api('Myth', 'GetStorageGroupDirs')
        sgdirs = sgxml['StorageGroupDirList']['StorageGroupDirs']['StorageGroupDir']
        retlist = []
        for sg in sgdirs:
            retlist.append([ sg['HostName'],sg['GroupName'],sg['DirName'] ])
        return retlist
    
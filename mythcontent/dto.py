
from mythcontent.data_access import VideoApi, VideoDao, TvRecordingApi
# from collections import OrderedDict
"""
This class is responsible for manipulating a single
MythTV recorded program.
"""
class TvRecording(object):
    def __init__(self, prog):
        self.prog = prog
    
    # some properties, for convenience:
    @property
    def title(self):
        return self.prog['Title']
    
    @property
    def filespec(self):
        return self.prog['FileSpec']
    
    @property
    def filename(self):
        return self.prog['FileName']
    @property
    def subtitle(self):
        return self.prog['SubTitle']
    
    @property
    def filesize(self):
        return self.prog['FileSize']
    
    @property
    def duration(self):
        return self.prog['Duration']
    
    @property
    def start_at(self):
        return self.prog['Recording']['StartTs']
    
    @property
    def end_at(self):
        return self.prog['Recording']['EndTs']
    
    @property
    def airdate(self):
        return self.prog['Airdate']
    
    @property
    def hostname(self):
        return self.prog['HostName']
    """
    Call the MythTV API to delete this
    recording.
    Pass:
      * self
    Returns:
      * True if successful, False if call failed (no such
      recording, for example)
    """
    def erase(self):
        api = TvRecordingApi()
        return api.erase(self.prog)
        
            
"""
Get a list of recorded tv programs from the API
class and pass along that list, with each element
wrapped in a TvRecording object.

In Java, this would probably be a static class.
"""
# def list_recordings():
#     api = TvRecordingApi()
#     return [ TvRecording(p) for p in api.tv_recordings ]             


"""

"""
class Video(object):
    """
    Constructor takes an optional parameter which is an OrderedDict
    containing information about a video in MythVideo.
    
    If this is not set in __init__, it can be set later by creating
    an empty Video and then loading the info from MythVideo, supplying
    a filename to the method call. EG:
    v = Video()
    v.load_from_mythvideo('CSI/1050_20151123333.mpg')
    """
    def __init__(self, vid=None):
        self.vid = vid
        
    
    """
    Use data_access.find_in_mythvideo() to see if a video with this
    filename already exists in MythVideo. If so, load our 'vid'
    attribute; othewise set 'vid' attribute to None.
    If a video with this filename already exists in MythVideo, set our
    'vid' attribute from it. Otherwise
    Check whether a video with a given filename is already in MythVideo.
    Pass:
      * file name (directory relative to videos storage group directory + os.sep + file name
    Return:
      * None.
    Side Effect:
      * Sets self's vid attribute.
    """
    def load_from_mythvideo(self, filename):
        self.vid = VideoApi().find_in_mythvideo(filename)   

    # Properties, for convenience:
    @property
    def id(self):
        return self.vid['Id']
    
    @property
    def title(self):
        return self.vid['Title']
    @title.setter
    def title(self, new_title):
        self.vid['Title'] = new_title

    @property
    def subtitle(self):
        return self.vid['SubTitle']
    @subtitle.setter
    def subtitle(self, new_subtitle):
        self.vid['SubTitle'] = new_subtitle
    
    @property
    def description(self):
        return self.vid['Description']
    @description.setter
    def description(self, new_description):
        self.vid['Description'] = new_description
    
    @property
    def adddate(self):
        return self.vid['AddDate']
    
    @property
    def length(self):
        return self.vid['Length']
    
    @property
    def playcount(self):
        return self.vid['PlayCount']
    
    @property
    def watched(self):
        return self.vid['Watched']
    
    @property
    def contenttype(self):
        return self.vid['ContentType']
    @contenttype.setter
    def contenttype(self, new_type):
        self.vid['ContentType'] = new_type
        
    @property
    def filename(self):
        return self.vid['FileName']

    @property
    def hostname(self):
        return self.vid['HostName']

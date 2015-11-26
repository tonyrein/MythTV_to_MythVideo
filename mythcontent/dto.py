
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
def list_recordings():
    api = TvRecordingApi()
    return [ TvRecording(p) for p in api.tv_recordings ]             


class Video(object):
    pass
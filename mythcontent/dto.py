
from mythcontent.data_access import VideoApi, VideoDao, TvRecordingApi
# from collections import OrderedDict
"""
This class is responsible for manipulating a single
MythTV recorded program.
"""
class TvRecording(object):
    def __init__(self, prog):
        self.prog = prog
    
    def erase(self):
        channel_id = self.prog['Channel']['ChanId']
        start_time = self.prog['Recording']['StartTs']
        api = TvRecordingApi()
        return api.erase(channel_id, start_time)
        
            
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
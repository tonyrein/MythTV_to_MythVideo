

from mythcontent.mythapi import MythApi

class TvRecording(object):
    def __init__(self, data):
        self._data = data # data should be a tv_recording named_tuple
        st_dir = MythApi().get_storage_dir(name=data.storage_group)
        self.filespec = st_dir + data.file_name # st_dir already ends with os.sep.
            
             
    
        

class Video(object):
    pass
import os

from mythcontent.dto import TvRecording, Video
from mythcontent.data_access import TvRecordingApi, VideoApi, VideoDao
from mythcontent.utils import copy_file_on_remote_host

class TvRecordingService(object):
    __instance = None # class attribute
    def __new__(cls):
        if TvRecordingService.__instance is None:
            TvRecordingService.__instance = object.__new__(cls)
            TvRecordingService.__instance._recordings = None
        return TvRecordingService.__instance
    
    def load_from_mythtv(self):
        api = TvRecordingApi()
        ret_list = []
        for r in api.tv_recordings:
            ret_list.append(TvRecording(r))
        return ret_list
        
    @property
    def recordings(self):
        if self._recordings is None:
            self._recordings = self.load_from_mythtv()
        return self._recordings
    
    def erase_recording(self, recording_to_erase):
        return recording_to_erase.erase()

class VideoService(object):
    __instance = None # class attribute
    def __new__(cls):
        if VideoService.__instance is None:
            VideoService.__instance = object.__new__(cls)
            VideoService.__instance._videos = None
        return VideoService.__instance
    
    def load_from_mythvideo(self):
        api = VideoApi()
        ret_list = []
        for v in api.videos:
            ret_list.append(Video(v))
        return ret_list
    
    """
    Is this item already known to us?
    """
    def __contains__(self, v):
        if isinstance(v,Video):
            return v in self.videos
        else: # assume it's a filename
            return v in [ n.filename for n in self.videos ]
        
    def add_to_mythvideo(self,filename):
        # already in our list?
        if filename in self.videos:
            raise Exception('File already in VideoService videos list.')
        # Is it already in MythVideo's content?
        v = None
        api = VideoApi()
        res = api.find_in_mythvideo(filename)
        if res is not None:
            # Already there -- save the result...
            v = Video(res)
        else:
            # try adding it...
            if api.add_to_mythvideo(filename): # MythTV API added file OK
                res = api.find_in_mythvideo(filename)
                if res is not None:
                    v = Video(res)
        # If the item is now in MythVideo (whether because
        # we succeeded in adding it, or because it was already there),
        # add it to our 'videos' attribute:
        if v is not None:
            self.videos.append(v)
    
    def in_mythvideo(self, filename):
        return VideoApi().find_in_mythvideo(filename)
        
    def add_video_from_tv_recording(self, recording):
        relative_filespec = recording.title + os.sep + recording.filename
        # Quit if it's already here...
        if relative_filespec in self:
            raise Exception("VideoService already contains {}".format(relative_filespec))
        # Or already in MythVideo:
        if self.in_mythvideo(relative_filespec):
            raise Exception("MythVideo already contains {}".format(relative_filespec))
        # Since it's not already there, add it. First step is to copy the file:
        api = VideoApi()
        dest_dir = api.video_directory + recording.title + os.sep
        copy_file_on_remote_host(recording.hostname, recording.filespec, dest_dir)
        # After physical file is in place, tell MythVideo about it:
        res = api.add_to_mythvideo(relative_filespec, recording.hostname)
        if res != True:
            raise Exception('Unknown failure adding {} to MythVideo'.format(recording.title))
        # Now add it to this VideoService object's list:
        res = api.find_in_mythvideo(relative_filespec)
        if res is None:
            raise Exception('Unknown failure adding {} to MythVideo'.format(recording.title))
        self.videos.append(Video(res))
        return True
        
    def update_metadata_from_tv_recording(self,recording):
        relative_filespec = recording.title + os.sep + recording.filename
        # following line should return a list of only 1:
        vid_list = VideoDao.objects.filter(filename=relative_filespec)
        if len(vid_list) != 1:
            raise Exception('Could not find {} - {} in database.'.format(recording.title,recording.subtitle))
        dao = vid_list[0]
        dao.title = recording.title
        dao.subtitle = recording.subtitle
        dao.contenttype='TELEVISION'
        orig_aired = recording.airdate
        

    @property
    def videos(self):
        if self._videos is None:
            self._videos = self.load_from_mythvideo()
        return self._videos

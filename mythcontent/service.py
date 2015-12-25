import os
import iso8601

from mythcontent.dto import TvRecording, Video
from mythcontent.data_access import TvRecordingApi, VideoApi
from mythcontent.utils import copy_file_on_remote_host

class TvRecordingService(object):
    __instance = None # class attribute
    def __new__(cls):
        if TvRecordingService.__instance is None:
            TvRecordingService.__instance = object.__new__(cls)
            TvRecordingService.__instance._recordings = None
            TvRecordingService.__instance._api = TvRecordingApi()
        return TvRecordingService.__instance
    
    def load_from_mythtv(self):
        ret_list = []
        for r in self._api.tv_recordings:
            ret_list.append(TvRecording(r))
        return ret_list
        
    @property
    def recordings(self):
        if self._recordings is None:
            self._recordings = self.load_from_mythtv()
        return self._recordings
    
    def contains_filename(self, fn):
        return fn in [ r.filename for r in self.recordings ]
     
    def erase_recording(self, recording_to_erase):
        return recording_to_erase.erase()

class VideoService(object):
    __instance = None # class attribute
    def __new__(cls):
        if VideoService.__instance is None:
            VideoService.__instance = object.__new__(cls)
            VideoService.__instance._videos = None
            VideoService.__instance._api=VideoApi()
            
            
        return VideoService.__instance
    
    def load_from_mythvideo(self):
#         api = VideoApi()
        ret_list = []
        for v in self._api.videos:
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
    
    """
    Given a filename, return a dto.Video object
    """
    def video_from_filename(self,filename):
        vlist = [ v for v in self.videos if  v.filename == filename]
        if len(vlist) == 0:
            return None
        else:
            return vlist[0]  
    
    def in_mythvideo(self, filename):
        return self._api.find_in_mythvideo(filename)

    def copy_tv_recording_file(self, recording):
        title_dir = recording.title.replace(' ','_') + os.sep
        relative_filespec = title_dir + recording.filename
        # Quit if it's already here...
        if relative_filespec in self:
            raise Exception("VideoService already contains {}".format(relative_filespec))
        # Or already in MythVideo:
        if self.in_mythvideo(relative_filespec):
            raise Exception("MythVideo already contains {}".format(relative_filespec))
        # Since it's not already there, add it. First step is to copy the file:
        dest_dir = self._api.video_directory + title_dir
        copy_file_on_remote_host(recording.hostname, recording.filespec, dest_dir)

    
    """
    This assumes that the disk file is already in place in
    the Video storage directory.
    """     
    def add_video_from_tv_recording(self, recording):
        title_dir = recording.title.replace(' ','_') + os.sep
        relative_filespec = title_dir + recording.filename
        res = self._api.add_to_mythvideo(relative_filespec, recording.hostname)
        if res != True:
            raise Exception('Unknown failure adding {} to MythVideo'.format(recording.title))
        # Now add it to this VideoService object's list:
        res = self._api.find_in_mythvideo(relative_filespec)
        if res is None:
            raise Exception('Unknown failure adding {} to MythVideo'.format(recording.title))
        self.videos.append(Video(res))
        return True
        
    def update_metadata_from_tv_recording(self,recording):
        orig_aired = iso8601.parse_date(recording.airdate)
        year = orig_aired.year
        title_dir = recording.title.replace(' ', '_') + os.sep
        v = self.video_from_filename(title_dir + recording.filename)
        if v is None:
            raise Exception("Could not find video with title {} and filename {}".format(recording.title, recording.filename))
        v.set_metadata(recording.title, recording.subtitle, year, recording.airdate)
        

    @property
    def videos(self):
        if self._videos is None:
            self._videos = self.load_from_mythvideo()
        return self._videos

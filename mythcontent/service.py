import os

from nonpublic.settings import ORPHANS
from mythcontent.dto import OrphanDto, ProgInfo, TvRecordingDto
from mythcontent.utils import stat_remote_host
from mythcontent.dao import MythApi, TvRecordingApi
from nonpublic.models import Orphan

class OrphanService(object):
    __instance = None
           
    def __new__(cls):
        if OrphanService.__instance is None:
            OrphanService.__instance = object.__new__(cls)
            OrphanService.__instance._orphan_list = None
        return OrphanService.__instance


    def load_orphan_list(self):
        hostname = ORPHANS['mythhost']
        dirname = ORPHANS['recording_dir']
        self._orphan_list = self.load_from_directory(hostname, dirname)
        
    """
    Read the contents of this file and make
    an OrphanDto from each row. Make a list
    of those objects.
    
    The file read by this method is for persistent storage
    and not for display.
    """
    def load_from_file(self,filename):
        pass
    """
    Make an OrphanDto from each file in
    this directory matching the pattern.
    """
    def load_from_directory(self, hostname, directory_name, filename_pattern='*.mpg'):
        # List all matching entries, but remove all which are not regular files:
        dirlist = stat_remote_host(hostname, directory_name + os.sep + filename_pattern, [ 'type', 'name', 'size' ])
        ret_list = []
        if dirlist and len(dirlist) > 0:
            ts = TvRecordingService()
            dirlist = [ {'name': f['name'], 'size': f['size'] } for f in dirlist if f['type'] == 'regular file']
            for f in dirlist:
                directory,filename = os.path.split(f['name'])
                if filename not in ts:
                    ret_list.append(OrphanDto(hostname, f['name'],f['size']))
        return ret_list
    
    """
    This takes the in-memory list of orphans
    and adds them to the Django sqlite database 'orphans' table.
    Intended to be used to initialize the database on the first run
    of the app.
    
    If 'override' is False (the default) the method will raise a
    ValueError if it's called when there are already records in
    the orphans table.
    
    If override is true, the method will attempt to add records
    to the orphans table even if there are pre-existing records;
    however, if the table's filename<->hostname unique constraint
    is violated, a django.db.IntegrityError will be raised.
    
    """
    def save_to_db(self, override=False):
        if not override and Orphan.objects.count() > 0:
            raise ValueError("OrphanService.save_to_db called with records already in orphans table.")
        for item in self.orphan_list:
            o = Orphan()
            o.hostname = item.hostname
            o.directory = item.directory
            o.filename = item.filename
            o.filesize = item.filesize
            o.duration = item.duration
            o.channel_id = item.channel_id
            o.channel_number = int(item.channel_number)
            o.channel_name = item.channel_name
            o.start_date = item.start_at.date()
            o.start_time = item.start_at.time()
            o.title = item.title
            o.subtitle = item.subtitle
            o.save()
       
    """
    Write the list of OrphanDto objects
    to the file.
    
    The file created by this method is for persistent storage
    and not for display. 
    """
    def save_to_file(self,filename):
        pass
    
    
    """
    Display the OrphanDto to the user and allow editing.
    Save changes to self's list of OrphanDto objects.
    
    Probably this should be in another package - it doesn't
    seem to belong in this layer.
    """
    def edit_orphan(self,orphan_dto):
        pass
    
    """
    Load a list of OrphanDto objects from a file which the user
    may have edited -- a spreadsheet in XLS or XLSX format.
    """
    def import_from_display(self,filename):
        pass
    
    @property
    def orphan_list(self):
        if self._orphan_list is None:
            self.load_orphan_list()
        return self._orphan_list

    

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
        for r in self._api.get_mythtv_recording_list():
            ret_list.append(TvRecordingDto(r))
        return ret_list
         
    @property
    def recordings(self):
        if self._recordings is None:
            self._recordings = self.load_from_mythtv()
        return self._recordings
    
    def __contains__(self,filename):
        return filename in [ r.filename for r in self.recordings ]
    
    def contains_filename(self, fn):
        return fn in [ r.filename for r in self.recordings ]
      
    def erase_recording(self, recording_to_erase):
        return recording_to_erase.erase()

class VideoService(object):
    pass

# import os
# import iso8601
# # from collections import namedtuple
# 
# from mythcontent.dto import TvRecording, Video
# from mythcontent.data_access import TvRecordingApi, VideoApi
# from mythcontent.utils import copy_file_on_remote_host, size_remote_file, delete_remote_file
# from nonpublic.settings import ORPHANS
# 
# # prog_info=namedtuple('prog_info', [ 'filename', 'date', 'dow', 'time', 'channel_number', 'channel_name', 'filesize', 'duration', 'title', 'subtitle' ])
# 
# 
# 
# class TvRecordingService(object):
#     __instance = None # class attribute
#     def __new__(cls):
#         if TvRecordingService.__instance is None:
#             TvRecordingService.__instance = object.__new__(cls)
#             TvRecordingService.__instance._recordings = None
#             TvRecordingService.__instance._api = TvRecordingApi()
#         return TvRecordingService.__instance
#     
#     def load_from_mythtv(self):
#         ret_list = []
#         for r in self._api.tv_recordings:
#             ret_list.append(TvRecording(r))
#         return ret_list
#         
#     @property
#     def recordings(self):
#         if self._recordings is None:
#             self._recordings = self.load_from_mythtv()
#         return self._recordings
#     
#     def contains_filename(self, fn):
#         return fn in [ r.filename for r in self.recordings ]
#      
#     def erase_recording(self, recording_to_erase):
#         return recording_to_erase.erase()
# 
# class VideoService(object):
#     __instance = None # class attribute
#     def __new__(cls):
#         if VideoService.__instance is None:
#             VideoService.__instance = object.__new__(cls)
#             VideoService.__instance._videos = None
#             VideoService.__instance._api=VideoApi()
#         return VideoService.__instance
#     
#     def load_from_mythvideo(self):
# #         api = VideoApi()
#         ret_list = []
#         for v in self._api.videos:
#             ret_list.append(Video(v))
#         return ret_list
#     
#     """
#     Is this item already known to us?
#     """
#     def __contains__(self, v):
#         if isinstance(v,Video):
#             return v in self.videos
#         else: # assume it's a filename
#             return v in [ n.filename for n in self.videos ]
#     
#     """
#     Given a filename, return a dto.Video object
#     """
#     def get_video_from_filename(self,filename):
#         vlist = [ v for v in self.videos if  v.filename == filename]
#         if len(vlist) == 0:
#             return None
#         else:
#             return vlist[0]  
#     
#     def in_mythvideo(self, filename):
#         return self._api.find_in_mythvideo(filename)
# 
# 
# 
#     def copy_tv_recording_file(self, recording):
#         title_dir = recording.title.replace(' ','_') + os.sep
#         relative_filespec = title_dir + recording.filename
#         # Quit if it's already here...
#         if relative_filespec in self:
#             raise Exception("VideoService already contains {}".format(relative_filespec))
#         # Or already in MythVideo:
#         if self.in_mythvideo(relative_filespec):
#             raise Exception("MythVideo already contains {}".format(relative_filespec))
#         # Since it's not already there, add it. First step is to copy the file:
#         dest_dir = self._api.video_directory + title_dir
#         copy_file_on_remote_host(recording.hostname, recording.filespec, dest_dir)
# 
# 
#     def copy_file_from_tv_to_video(self, pinf, source_dir):
#         relative_filespec = pinf.relative_filespec()
#         if relative_filespec in self:
#             raise Exception("VideoService already contains {}".format(relative_filespec))
#         if self.in_mythvideo(relative_filespec):
#             raise Exception("MythVideo already contains {}".format(relative_filespec))
#         # Since it's not already there, do the copy:
#         dest_dir = self.video_directory() + pinf.subdir() + os.sep
#         source_filespec = source_dir + os.sep + pinf.filename
#         hostname = ORPHANS['mythhost']
#         copy_file_on_remote_host(hostname, source_filespec, dest_dir)
#         # Now compare source and dest file sizes to see if copy was successful:
#         size_source = size_remote_file(hostname, source_filespec)
#         size_dest = size_remote_file(hostname, pinf.full_filespec())
#         return size_source - size_dest
#         
#         
#     def add_video_from_prog_info(self,pinf):
#         filespec = pinf.relative_filespec()
#         if not self.in_mythvideo(filespec):
#             if not self._api.add_to_mythvideo(filespec):
#                 raise Exception('Unknown failure adding to MythVideo: {}: {}-{}'.
#                                 format(pinf.filename, pinf.title, pinf.subtitle)
#                                 )
#             res = self._api.find_in_mythvideo(filespec)
#             if res is None:
#                 raise Exception('Unknown failure adding to MythVideo: {}: {}-{}'.
#                                 format(pinf.filename, pinf.title, pinf.subtitle)
#                                 )
#             self.videos.append(Video(res))
#             
#                 
#     """
#     This assumes that the disk file is already in place in
#     the Video storage directory.
#     """     
#     def add_video_from_tv_recording(self, recording):
#         title_dir = recording.title.replace(' ','_') + os.sep
#         relative_filespec = title_dir + recording.filename
#         res = self._api.add_to_mythvideo(relative_filespec, recording.hostname)
#         if res != True:
#             raise Exception('Unknown failure adding {} to MythVideo'.format(recording.title))
#         # Now add it to this VideoService object's list:
#         res = self._api.find_in_mythvideo(relative_filespec)
#         if res is None:
#             raise Exception('Unknown failure adding {} to MythVideo'.format(recording.title))
#         self.videos.append(Video(res))
#         return True
#         
#     def update_metadata_from_tv_recording(self,recording):
#         orig_aired = iso8601.parse_date(recording.airdate)
#         year = orig_aired.year
#         title_dir = recording.title.replace(' ', '_') + os.sep
#         v = self.get_video_from_filename(title_dir + recording.filename)
#         if v is None:
#             raise Exception("Could not find video with title {} and filename {}".format(recording.title, recording.filename))
#         v.set_metadata(recording.title, recording.subtitle, year, recording.airdate)
#     
#     
#     def update_metadata_from_proginfo(self,pinf):
#         year = str(pinf.date.year)
#         v = self.get_video_from_filename(pinf.relative_filespec())
#         if v is None:
#             raise Exception(
#                     "Could not find video with title {} and filename {}"
#                     .format(pinf.title, pinf.filename)
#                     )
#         v.set_metadata(pinf.title, pinf.subtitle, year, pinf.date, pinf.duration)
#         
#     def delete_video_from_proginfo(self,hostname,pinf,force_delete=False):
#         if not pinf.video_made:
#             if not force_delete:
#                 return
#         return delete_remote_file(hostname, pinf.full_filespec())       
#         
#     def video_directory(self):
#         return  self._api.video_directory
#     
#     @property
#     def videos(self):
#         if self._videos is None:
#             self._videos = self.load_from_mythvideo()
#         return self._videos

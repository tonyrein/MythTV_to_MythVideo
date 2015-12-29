"""
The code in this file is concerned with recovering
"orphan" tv recordings. The context is as follows:
I had a failure of the OS disk in my MythTV backend. I
built a new system, but when I attempted to restore the
database, I found that the recent backups were invalid,
and that the newest valid backup was eight months old.
I restored from that backup, with the result that I had
lots of files in my recording directory that MythTV didn't
know about.

The simplest approach to recovery seems to be to move
the files into the video storage directory and create
MythVideo entries -- the database structure for this is
much simpler than that for tv recordings.

Step 1 is to create a list of files in a convenient format,
and fill in information about each file. From the file name,
the channel and the date and time of airing can be derived,
and the file size lets you know the approximate duration.
This information was gathered into a CSV file.

Step 2 is to manually play each file of interest, figure out
what the show is, and add that information to the CSV file

Step 3 is to move each file from the recording directory
to the video directory and invoke the MythAPI
Video.AddVideo call to add the file to MythVideo.

Step 4 is to fill in the metadata (derived in steps 1 and 2)
for the video.

Step 5 is cleanup -- delete the original files.

"""
from collections import namedtuple
import datetime
import csv
import os.path
from mythcontent.data_access import ChannelApi
from mythcontent.dto import ProgInfo
from mythcontent.utils import list_files_on_remote_host
from mythcontent.utils import copy_file_on_remote_host
from mythcontent.service import TvRecordingService, VideoService
from nonpublic.settings import ORPHANS
# Use prog_info for stuff that's to be displayed and manually edited. That is,
# This is used to generate and then read a CSV file that will be shown to the
# user, allowing the user to fill in additional information for each file.
# prog_info=namedtuple('prog_info', [ 'filename', 'date', 'dow', 'time', 'channel_number', 'channel_name', 'filesize', 'duration', 'title', 'subtitle' ])

# Use vid_info to hold the information which will be inserted into MythVideo.
# For this, we don't need channel, dow, or file size.
# vid_info=namedtuple('vid_info','filename title subtitle year releasedate duration subdir')
# REC_FILENAME_DATE_FORMAT='%Y%m%d%H%M%S'
# BYTES_PER_MINUTE=38928300 # approx. 39 million bytes/minute in a
#                             # SD Mythtv recording
# def metadata_from_vid_info(vi):
#     title=vi.title
#     subtitle=vi.subtitle
#     year=vi.date.split('/')[0] # date is in format '2015/12/23'
#     # dto.Video.set_metadata() expects releasedate to be UTC. Get
#     # that from the filename. The filename is of format '1003_20151222120000...
#     # where the portion right after the '_' is the YYYYmmdd
#     dt_portion=vi.filename.split('_')[1][:14]
#     releasedate=datetime.datetime.strptime(dt_portion,REC_FILENAME_DATE_FORMAT)
#     length=vi.duration
#     return (title,subtitle,year,releasedate,length)

"""
Parses file name and file size to fill in some basic
information about the program.
The file name is of the form: 
  CCCC_YYYYMMDDHHMMSS.mpg, where CCCC=channel id, YYYY is year,
  MM is month, DD day of month, HH hours, MM minutes, and SS seconds.
From the channel id we can make a MythTV API call to get the channel name
and channel number, and then use strptime to get a datetime from the rest.

From the datetime we can derive the date, the time, and the day of week.

Then, from the file size, we guess the duration.
  
"""
class Rescuer(object):
    def __init__(self,hostname=None,recording_dir=None,metadata_file=None):
        if hostname is None:
            hostname = ORPHANS['mythhost']
        if recording_dir is None:
            recording_dir = ORPHANS['recording_dir']
        if metadata_file is None:
            metadata_file = ORPHANS['metadata_file']
        self.hostname = hostname
        self.recording_dir = recording_dir
        self.metadata_file = metadata_file
        self.video_dir = VideoService().video_directory()
        
        # If metadata_file already exists, read it. If not,
        # assume this is the first run and create it.
        if os.path.isfile(self.metadata_file):
            self.file_list = self.read_metadata_file()
        else:
            self.file_list = self.scan_recording_directory()
            self.save_metadata_file()

    """
    Parses file name and file size to fill in some basic
    information about the program.
    The file name is of the form: 
      CCCC_YYYYMMDDHHMMSS.mpg, where CCCC=channel id, YYYY is year,
      MM is month, DD day of month, HH hours, MM minutes, and SS seconds.
    From the channel id we can make a MythTV API call to get the channel name
    and channel number, and then use strptime to get a datetime from the rest.
    
    From the datetime we can derive the date, the time, and the day of week.
    
    Then, from the file size, we guess the duration.
      
    """
#     def prog_info_from_file(self,filename,filesize):
#         (chanid,rest) = filename.split('_')
#         channel_info = ChannelApi().get_channel_info(chanid)
#         channel_number = channel_info['ChanNum']
#         channel_name = channel_info['ChannelName']
#         dt_portion=rest[:14]
#         dt=datetime.datetime.strptime(dt_portion,REC_FILENAME_DATE_FORMAT)
#         airdate=dt.date()
#         airtime=dt.time()
#         dow="{:%a}".format(dt) # day of week as locale abbreviation
#         duration=round(int(filesize)/BYTES_PER_MINUTE)
#         # We don't know the title or subtitle yet.
#         return prog_info( [filename, airdate, dow, airtime, channel_number,
#                              channel_name, filesize, duration, '', '']
#                          )
                
    
    """
    Reads list of files in recording directory.
    Returns list of prog_info objects
    """
    def scan_recording_directory(self):
        ts=TvRecordingService()
        fl=list_files_on_remote_host(self.hostname, self.recording_dir + os.sep + '*.mpg')
        # filter out the ones that aren't regular files and the ones that are not in fact
        # orphans. Save only the file name and size:
        orphan_files = []
        for f in fl:
            if f[0] == 'regular file':
                n=f[1].split(os.sep)[-1]
                if not ts.contains_filename(n):
                    pi = ProgInfo.make_proginfo_from_filename_and_size(n, f[2])
                    orphan_files.append(pi)
        return orphan_files
    
    def read_metadata_file(self):
        ret_list = []
        with open(self.metadata_file,'r') as infile:
            reader=csv.reader(infile)
            next(reader) # skip headers
            for row in reader:
                pi = ProgInfo.make_proginfo_from_csv_row(row)
                ret_list.append(pi)
        return ret_list
    
    def save_metadata_file(self):
        with open(self.metadata_file,'w') as outfile:
            writer=csv.writer(outfile)
            # write headers:
            writer.writerow(ProgInfo.fieldnames())
            for f in self.file_list:
                writer.writerow(f.as_row())
#                 writer.writerow( list(f._asdict().values()   ))
        
    def is_in_collection(self,filename):
        # Return the item if it's there; otherwise return False
        return next(
                    (item for item in self._file_list if item.filename == filename),
                    False
                    )


    """
    Copy a recording's file from the tv recordings directory to the
    video directory. This assumes that the two are either on the
    same host, or, if network-mounted shares, are accessible from
    the same host with the "cp" command.
    
    The destination will be a subdirectory under the video storage
    group directory; the directory name will be generated from the
    recording's title, with spaces replaced by underscores.
    
    Pass:
        pinf: a ProgInfo object
    """
    def copy_file_to_video_dir(self,pinf):
        source_file = self.recording_dir + os.sep + pinf.filename
        dest_dir = self.video_dir + os.sep + pinf.subdir() + os.sep
        copy_file_on_remote_host(self.hostname, source_file, dest_dir)

    """
    Assumes file has already been copied into the video storage group directory.
    First check to see if MythTV already knows about this file; if not, tell
    MythTV to add it.
    """    
    def add_video_entry(self,pinf):
        filespec = pinf.relative_filespec()
        vs = VideoService()
#         if not vs.in_mythvideo(filespec):
            
        
    
    
        
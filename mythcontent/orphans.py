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
import os
import os.path
from mythcontent.data_access import ChannelApi
from mythcontent.utils import list_files_on_remote_host
from mythcontent.service import TvRecordingService

# Use prog_info for stuff that's to be displayed and manually edited. That is,
# This is used to generate and then read a CSV file that will be shown to the
# user, allowing the user to fill in additional information for each file.
prog_info=namedtuple('prog_info','filename date dow time channel_number channel_name filesize duration title subtitle')

# Use vid_info to hold the information which will be inserted into MythVideo.
# For this, we don't need channel, dow, or file size.
vid_info=namedtuple('vid_info','filename title subtitle year releasedate duration subdir')
REC_FILENAME_DATE_FORMAT='%Y%m%d%H%M%S'
BYTES_PER_MINUTE=38928300 # approx. 39 million bytes/minute in a
                            # SD Mythtv recording
def metadata_from_vid_info(vi):
    title=vi.title
    subtitle=vi.subtitle
    year=vi.date.split('/')[0] # date is in format '2015/12/23'
    # dto.Video.set_metadata() expects releasedate to be UTC. Get
    # that from the filename. The filename is of format '1003_20151222120000...
    # where the portion right after the '_' is the YYYYmmdd
    dt_portion=vi.filename.split('_')[1][:14]
    releasedate=datetime.datetime.strptime(dt_portion,REC_FILENAME_DATE_FORMAT)
    length=vi.duration
    return (title,subtitle,year,releasedate,length)

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
    def __init__(self,hostname,recording_dir,metadata_file, first_run = False):
        if not hostname or not recording_dir or not metadata_file:
            raise ValueError("You must supply a hostname, a recording storage directory, and a metadata file name.")
        self.hostname=hostname
        self.recording_dir=recording_dir
        self.metadata_file=metadata_file
        # file_list is a list of prog_info namedtuples
        if first_run:
            self.file_list = self.scan_recording_directory()
            self.save_metadata_file()
        else:
            self.file_list = self.read_metadata_file()


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
    def prog_info_from_file(self,filename,filesize):
        (chanid,rest) = filename.split('_')
        channel_info = ChannelApi().get_channel_info(chanid)
        channel_number = channel_info['ChanNum']
        channel_name = channel_info['ChannelName']
        dt_portion=rest[:14]
        dt=datetime.datetime.strptime(dt_portion,REC_FILENAME_DATE_FORMAT)
        airdate=dt.date()
        airtime=dt.time()
        dow="{:%a}".format(dt) # day of week as locale abbreviation
        duration=round(int(filesize)/BYTES_PER_MINUTE)
        # We don't know the title or subtitle yet.
        return prog_info( * (filename, airdate, dow, airtime, channel_number,
                             channel_name, filesize, duration, '', '')
                         )
                
    
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
                    orphan_files.append(
                                   self.prog_info_from_file(n, f[2])
                               )
        return orphan_files
    
    def read_metadata_file(self):
        pass

    
    def save_metadata_file(self):
        with open(self.metadata_file,'w') as outfile:
            writer=csv.writer(outfile)
            # write headers:
            writer.writerow(prog_info._fields)
            for f in self.file_list:
                writer.writerow( list(f._asdict().values()   ))
        
    def is_in_collection(self,filename):
        # Return the item if it's there; otherwise return False
        return next(
                    (item for item in self._file_list if item['filename'] == filename),
                    False
                    )
                   
                   
        
    
    
    
        
    
    
        
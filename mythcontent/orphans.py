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
# from collections import namedtuple
# import datetime
import csv
import os.path
# from mythcontent.data_access import ChannelApi
from mythcontent.dto import ProgInfo
from mythcontent.utils import list_files_on_remote_host
from mythcontent.service import TvRecordingService, VideoService
from nonpublic.settings import ORPHANS

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
        vs = VideoService()
        self.video_dir = vs.video_directory()
        
        # If metadata_file already exists, read it. If not,
        # assume this is the first run and create it.
        if os.path.isfile(self.metadata_file):
            self.file_list = self.read_metadata_file()
        else:
            self.file_list = self.scan_recording_directory()
            self.save_metadata_file()

    """
    Reads list of files in recording directory.
    Returns list of ProgInfo objects
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
    """
    Reads metadata csv file (presumably already edited by user)
    and returns list of ProgInfo objects.
    """
    def read_metadata_file(self):
        ret_list = []
        with open(self.metadata_file,'r') as infile:
            reader=csv.reader(infile)
            next(reader) # skip headers
            for row in reader:
                pi = ProgInfo.make_proginfo_from_csv_row(row)
                ret_list.append(pi)
        return ret_list
    
    """
    Saves current list of ProgInfo objects to metadata csv
    file. Wipes out previous file contents!
    """
    def save_metadata_file(self):
        with open(self.metadata_file,'w') as outfile:
            writer=csv.writer(outfile)
            # write headers:
            writer.writerow(ProgInfo.fieldnames())
            for f in self.file_list:
                writer.writerow(f.as_row())
        
    def is_in_collection(self,filename):
        # Return the item if it's there; otherwise return False
        return next(
                    (item for item in self._file_list if item.filename == filename),
                    False
                    )

    def rescue(self,pinf,redo=False):
        # First, has a video already been made
        # for this item? If so, don't proceed
        # unless 'redo' is True:
        if pinf.video_made:
            if redo == False:
                return
        # Next, copy this item's file from into the appropriate
        # video directory.
        vs = VideoService()
        source_dir = ORPHANS['recording_dir']
        # res will be zero if copy went OK...
        res = vs.copy_file_from_tv_to_video(pinf, source_dir)
        if res != 0:
            raise Exception("Unknown error copying {}-{} ({}) to video directory"
                            .format(pinf.title,pinf.subtitle,pinf.filename))
        # Now tell MythTV about the file we just inserted...
        vs.add_video_from_prog_info(pinf)
        # and set the new video entry's metadata:
        vs.update_metadata_from_proginfo(pinf)
        # If all the above was successful, mark this ProgInfo as done:
        pinf.video_made = True
        
    def delete_prog(self,pinf):
        vs = VideoService()
        (exit_status,stdout,stderr) = vs.delete_video_from_proginfo(
                            self.hostname, pinf, force_delete = False
                            )
        if exit_status == 0:
            self.file_list.remove(pinf)


        
        
    
    
        
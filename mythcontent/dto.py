import datetime
import os

from mythcontent.data_access import VideoApi, VideoDao, TvRecordingApi
from mythcontent.utils import iso_to_tz_aware, ensure_tz_aware, ensure_utc, utc_dt_to_local_dt
from mythcontent.constants import REC_FILENAME_DATE_FORMAT, BYTES_PER_MINUTE
from mythcontent.data_access import ChannelApi
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
        
class ProgInfo(object):
    def __init__(self, row=None, tv_dir=None):
        if row is None:
            [ self.filename, self.date, self.dow, self.time, self.channel_number,
              self.channel_name, self.filesize, self.duration, self.title,
              self.subtitle, self.video_made ] = [ None ]* 11
        else:
            [ self.filename, self.date, self.dow, self.time, self.channel_number,
              self.channel_name, self.filesize, self.duration, self.title,
              self.subtitle, self.video_made ] = row
        self.tv_dir = tv_dir
    
    @staticmethod
    def fieldnames():
        return [ 'filename','date','dow','time','channel_number','channel_name',
                'filesize','duration','title','subtitle','video_made'
                ]
    
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
    @staticmethod
    def row_from_file_name_and_size(filename,filesize):
        (chanid,rest) = filename.split('_')
        channel_info = ChannelApi().get_channel_info(chanid)
        channel_number = channel_info['ChanNum']
        channel_name = channel_info['ChannelName']
        dt_portion=rest[:14]
        utc_dt=datetime.datetime.strptime(dt_portion,REC_FILENAME_DATE_FORMAT)
        utc_dt = ensure_tz_aware(utc_dt)
        local_dt = utc_dt_to_local_dt(utc_dt)
        airdate=local_dt.date()
        airtime=local_dt.time()
        dow="{:%a}".format(airdate) # day of week as locale abbreviation
        filesize = int(filesize)
        duration = round(filesize/BYTES_PER_MINUTE)
        return [ filename, airdate, dow, airtime, channel_number, channel_name,
                filesize, duration,
                '', # don't know title just from filename
                '', # or subtitle
                False]
    
    @staticmethod
    def make_proginfo_from_filename_and_size(filename,filesize,tv_dir=None):
        r = ProgInfo.row_from_file_name_and_size(filename,filesize)
        return ProgInfo(row=r,tv_dir)
    
    @staticmethod
    def make_proginfo_from_csv_row(csv_row,tv_dir=None):
        r = ProgInfo.row_from_csv_row(csv_row)
        return ProgInfo(row=r)    
    """
    When a csv file containing information about a recorded
    program is read, this method converts each row from the
    file from strings into other types, as appropriate.
    """
    @staticmethod
    def row_from_csv_row(csv_row):
        row = csv_row
        s = row[1][:10].replace('-','/')
        airdate = datetime.datetime.strptime(s, '%Y/%m/%d')
        row[1] = airdate
        airtime = datetime.datetime.strptime(row[3], '%H:%M:%S').time()
        row[3] = airtime
        filesize = int(row[6])
        row[6] = filesize
        duration = int(row[7])
        row[7] = duration
        # Change '1' and '0' into True and False:
        video_made = int(row[10]) != 0
        row[10] = video_made
        return row
        
            
    def video_subdir(self):
        return self.title.replace(' ','_')
    
    def video_relative_filespec(self):
        return self.subdir() + os.sep + self.filename
    
    def video_full_filespec(self):
        return VideoApi().video_directory + self.relative_filespec()       
    
    def tv_full_filespec(self):
            pass
        
    def as_row(self):
        return [ self.filename, self.date, self.dow, self.time, self.channel_number,
             self.channel_name, self.filesize, self.duration, self.title,
             self.subtitle, '1' if self.video_made else '0'  ]          

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
    @adddate.setter
    def adddate(self,new_date):
        self.vid['AddDate'] = new_date
    
    @property
    def releasedate(self):
        return self.vid['ReleaseDate']
    @releasedate.setter
    def releasedate(self,new_date):
        self.vid['ReleaseDate'] = new_date
    
    @property
    def length(self):
        return self.vid['Length']
    @length.setter
    def length(self,new_length):
        if new_length < 0:
            raise ValueError('Video length must be a number greater than zero.')
        self.vid['Length'] = new_length
    
    @property
    def year(self):
        return self.vid['Year']
    @year.setter
    def year(self, new_year):
        self.vid['Year'] = new_year
    
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
    
    """
    This is really the filespec, not just
    the name. It includes the directory portion
    (if any) relative to the video storage
    group directory.
    """    
    @property
    def filename(self):
        return self.vid['FileName']
    @filename.setter
    def filename(self,new_name):
        self.vid['FileName'] = new_name
        

    @property
    def hostname(self):
        return self.vid['HostName']
    
   
    def set_metadata(self, title, subtitle, year, release_date,length=0,contenttype='TELEVISION'):
        # following line should return a list of only 1:
        vid_list = VideoDao.objects.filter(filename=self.filename)
        if len(vid_list) != 1:
            raise Exception('Could not find {} - {} in database.'.format(title,subtitle))
        dao = vid_list[0]
        dao.title = title
        dao.subtitle = subtitle
        dao.contenttype=contenttype
        dao.year = year
        # Need to convert insertdate and releasedate to "aware" date/time to
        # avoid a warning when saving:
        dao.insertdate = iso_to_tz_aware(dao.insertdate)
        dao.releasedate = iso_to_tz_aware(release_date)
        dao.length = length
        dao.save()
        # set our own metadata also, as well as that in the database:
        self.title = title
        self.subtitle = subtitle
        self.year = year
        self.releasedate = dao.releasedate
        self.adddate = dao.insertdate
        
        

import os.path

from django.core.urlresolvers import reverse
from django.db import models

# Create your models here.

class Orphan(models.Model):
    intid = models.AutoField(primary_key=True)
    hostname = models.CharField(max_length=128)
    title = models.CharField(max_length=128, blank=True, default='')
    directory = models.CharField(max_length=256)
    filename = models.CharField(max_length=20)
    filesize = models.BigIntegerField(blank=True, default=0)
    duration = models.SmallIntegerField(blank=True, default=0)
    start_date = models.DateField()
    start_time = models.TimeField()
    subtitle = models.TextField(blank=True, default='')
    channel_id = models.CharField(max_length=4)
    channel_number = models.SmallIntegerField()
    channel_name = models.CharField(max_length=256)
     
    @property
    def samplename(self): #"Calculated" field -- name of sample file
        return os.path.splitext(self.filename)[0] + '.ogv'
    @classmethod
    def db_name(cls):
        return 'default'
 
     
    def get_absolute_url(self):
        return reverse('orphan_detail', args=[str(self.intid)])
    
    class Meta:
        managed = True
        db_table = 'orphans'
        # The combination of hostname and filename must be unique. This will be enforced both by model
        # validation and at the database level. If an attempt is made to save a model item which violates
        # this contraint, a django.db.IntegrityError will be raised.
        unique_together = ('hostname', 'filename')


"""
In order to ensure that MythTV's API has a chance to
create the "magic values" (notably, the hash), we
will write a create() method for this class, as
explained here:
https://docs.djangoproject.com/en/1.8/ref/models/instances/#django.db.models.Model
The only downside is that clients will have to use this create()
method instead of simply instantiating an object.

The normal flow would be:
   * In the create() method:
       * Create an object. Set its filename field
       * Call the API Video/GetVideoByFileName call
            -- If it returns 'not found':
                copy file to Videos storage group, if necessary
                use Video/AddVideo to add this to MythVideo.
       * Get the DB record corresponding to this video and fill in
            our values from it

   * Update other values as desired (metadata)
   * call save()
   
   Another issue is that MySQL/MariaDB don't store the timezone in date/time fields.
   Therefore, if your Django site has "USE_TZ=True," you get a warning about "naive"
   datetime values when you save a Video object back to the database.
   To get around this, it's necessary to convert the datetime value into a timezone-
   aware datetime before saving, by doing something like:
   
   (assume "v" is a Video object)
   
   from django.utils import timezone
   import pytz
   d = v.insertdate
   timezone.make_aware(d,pytz.timezone('UTC')
   v.insertdate = d
"""
class VideoDaoOrig(models.Model):
    @classmethod
    def db_name(cls):
        return 'mythcopy'
    
    intid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    subtitle = models.TextField()
    tagline = models.CharField(max_length=255, blank=True, null=True)
    director = models.CharField(max_length=128)
    studio = models.CharField(max_length=128, blank=True, null=True)
    plot = models.TextField(blank=True, null=True)
    rating = models.CharField(max_length=128)
    inetref = models.CharField(max_length=255)
    collectionref = models.IntegerField()
    homepage = models.TextField()
    year = models.IntegerField()
    releasedate = models.DateField()
    userrating = models.FloatField()
    length = models.IntegerField()
    playcount = models.IntegerField()
    season = models.SmallIntegerField()
    episode = models.SmallIntegerField()
    showlevel = models.IntegerField()
    filename = models.TextField()
    hash = models.CharField(max_length=128)
    coverfile = models.TextField()
    childid = models.IntegerField()
    browse = models.IntegerField()
    watched = models.IntegerField()
    processed = models.IntegerField()
    playcommand = models.CharField(max_length=255, blank=True, null=True)
    category = models.IntegerField()
    trailer = models.TextField(blank=True, null=True)
    host = models.TextField()
    screenshot = models.TextField(blank=True, null=True)
    banner = models.TextField(blank=True, null=True)
    fanart = models.TextField(blank=True, null=True)
    insertdate = models.DateTimeField(blank=True, null=True)
    contenttype = models.CharField(max_length=43)
    
    class Meta:
        managed = False
        db_table = 'videometadata'
        
    @classmethod
    def create(cls, filename=None):
        v = cls(filename)
        #############################################
        # If filename is not None, then call the    #
        # API Video/GetVideoByFileName call.        #
        # If the API call fails, throw an exception.#
        # If MythTV API Video/GetVideoByFileName    #
        # returns success with this filename,       #
        # find corresponding record in DB and       #
        # set our values from that record.          #
        # If failure, throw an exception            #
        #                                           #
        # If filename is not None, but the          #
        # GetVideoByFileName call returns "not      #
        # found," then:                             #
        #   1. copy filename to the Videos SG, if   #
        #       needed                              #
        #   2. call Video/AddVideo                  #
        #   3. Get the row from db, set our values. #
        #############################################
        return v
        

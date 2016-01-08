import os.path

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
    class Meta:
        managed = True
        db_table = 'orphans'
#         This is enforced at the database level and by model validation. If you try to save a model with a
#         duplicate value in a unique field, a django.db.IntegrityError will be raised by the model’s save() method.
        unique_together = ('hostname', 'filename')
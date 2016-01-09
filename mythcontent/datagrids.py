import os.path

import django_tables2 as tables
from django_tables2.utils import Accessor, A  # alias for Accessor
from nonpublic.models import Orphan
from django.template import defaultfilters
from django.utils.safestring import mark_safe
from django.utils.html import escape

class EditButtonColumn(tables.Column): 
    empty_values = list() 
    def render(self, value, record): 
        return mark_safe('<button id="{}" class="btn btn-info">Edit</button>'.format(escape(record.intid)) )


class OrphanTable(tables.Table):
#     play=tables.TemplateColumn("""<a href={% url 'mythcontent-edit-orphan' '27' %}>Edit</a>""", orderable=False)
#     play = tables.LinkColumn('play_file', text='View File', args=[A('pk')], attrs={ 'target': '_blank' }, empty_values=() )
#     selection = tables.CheckBoxColumn(accessor="pk", orderable=False)
#     edit = EditButtonColumn()
    play = tables.LinkColumn('mythcontent:mythcontent-edit-orphan', text='Edit Entry', args=[ A('intid')], attrs={ 'target': '_blank' }, empty_values=(), orderable=False )
    samplename = tables.Column()
    # Format filesize and time columns
    def render_filesize(self,value):
        return defaultfilters.filesizeformat(value)
    def render_start_time(self,value):
        return defaultfilters.time(value, 'h:i A')

    class Meta:
        model = Orphan
        # add class="paleblue" to <table> tag...
        attrs = { 'class': 'paleblue' }
        exclude = ('samplename','intid', 'channel_id','filename','hostname','directory')
        sequence = ('play','channel_number', 'channel_name', 'start_date', 'start_time','filesize','duration','title','subtitle')

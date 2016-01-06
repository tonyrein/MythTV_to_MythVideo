
import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from nonpublic.models import Orphan
from django.utils.safestring import mark_safe
from django.utils.html import escape

class EditButtonColumn(tables.Column): 
    empty_values = list() 
    def render(self, value, record): 
        return mark_safe('<button id="{}" class="btn btn-info">Edit</button>'.format(escape(record.intid)) )


class OrphanTable(tables.Table):
#     selection = tables.CheckBoxColumn(accessor="pk", orderable=False)
#     edit = EditButtonColumn()
    play = tables.LinkColumn('play_file', text='View File', args=[A('pk')], attrs={ 'target': '_blank' })
    class Meta:
        model = Orphan
        # add class="paleblue" to <table> tag...
        attrs = { 'class': 'paleblue' }
        sequence = ('play','channel_number', 'channel_name', 'start_date', 'start_time','filesize','duration','title','subtitle')
        exclude = ('intid', 'channel_id','filename','hostname','directory')
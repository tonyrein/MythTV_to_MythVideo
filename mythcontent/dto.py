from collections import namedtuple

storage_group = namedtuple('StorageDir', ['host','name','directory'])

tv_recording = namedtuple('TVRecording', ['title', 'subtitle', 'description', 'start_at', 'duration', 'channel_number', 'host',
    'storage_group', 'file_name', 'file_size', 'channel_id', 'start_ts' ])

myth_video = namedtuple(
                    'MythVideo',
                     ['title','subtitle','description','length','play_count','season','episode','watched','content_type','file_name','host',]
                     )

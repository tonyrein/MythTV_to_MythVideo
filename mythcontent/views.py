from django.shortcuts import render
from django.http import HttpResponse

from .mythapi import MythApi
# Create your views here.

"""
Display a list of recorded TV programs
"""
def index(request):
    return HttpResponse("This page will display a list of TV programs.")

def videos(request):
    api = MythApi()
    video_list = api.get_mythvideo_list()
    context = {'video_list': video_list}
    return render(request, 'mythcontent/videos.html', context)
#     return HttpResponse("This page will display a list of videos.")
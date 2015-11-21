from django.shortcuts import render
from django.http import HttpResponse

from .mythapi import MythApi
# Create your views here.

"""
Display a list of recorded TV programs
"""
def index(request):
    api = MythApi()
    tv_program_list = api.get_myth_tv_program_list()
    # save list in session:
    request.session['tv_program_list'] = tv_program_list
    context = { 'tv_program_list': tv_program_list, 'session': request.session }
    return render(request, 'mythcontent/index.html', context)

def videos(request):
    api = MythApi()
    video_list = api.get_mythvideo_list()
    context = {'video_list': video_list}
    return render(request, 'mythcontent/videos.html', context)
#     return HttpResponse("This page will display a list of videos.")
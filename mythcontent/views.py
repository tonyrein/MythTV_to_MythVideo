from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

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
    return render(request, 'mythcontent/index.html')

def videos(request):
    api = MythApi()
    video_list = api.get_mythvideo_list()
    context = {'video_list': video_list}
    return render(request, 'mythcontent/videos.html', context)

def process_moves(request):
    if request.method != 'POST':
        raise Exception("Must use Post with this view")
    checkboxlist = request.POST.getlist('selected_programs')
    template = loader.get_template('mythcontent/process_moves.html')
    context = RequestContext(request, {'selected_programs': checkboxlist, })
    return HttpResponse(template.render(context))
#    return render(request, 'mythcontent/process_moves.html')
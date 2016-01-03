from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from mythcontent.service import OrphanService, TvRecordingService, VideoService


# Create your views here.

"""
Display a list of recorded TV programs
"""
# def index(request):
#     api = MythApi()
#     tv_program_list = api.get_myth_tv_program_list()
#     # save list in session:
#     request.session['tv_program_list'] = tv_program_list
#     template = loader.get_template('mythcontent/index.html')
#     context = RequestContext(request,)
#     return HttpResponse(template.render(context))
# #     return render(request, 'mythcontent/index.html')


def index(request):
    ts = TvRecordingService()
    tv_program_list = ts.recordings
    # save list in session:
    request.session['tv_program_list'] = tv_program_list
    template = loader.get_template('mythcontent/index.html')
    context = RequestContext(request,)
    return HttpResponse(template.render(context))
#     return render(request, 'mythcontent/index.html')

def orphans(request):
    os = OrphanService()
    request.session['orphan_list'] = os.orphan_list
    template = loader.get_template('mythcontent/orphans.html')
    context = RequestContext(request,)
    return HttpResponse(template.render(context))

def videos(request):
    pass
#     vs = VideoService()
#     video_list = api.get_mythvideo_list()
#     template = loader.get_template('mythcontent/videos.html')
#     context = RequestContext(request, {'video_list': video_list, })
#     return HttpResponse(template.render(context))
# #     return render(request, 'mythcontent/videos.html', context)
# 
# def process_moves(request):
#     if request.method != 'POST':
#         raise Exception("Must use Post with this view")
#     checkboxlist = request.POST.getlist('selected_programs')
#     # Each element in the list is channel_id....start_ts
#     selected_programs = []
#     # Get list of programs as namedtuples:
#     sess_list = request.session['tv_program_list']
#     for b in checkboxlist:
#         channel_id, start_ts = b.split('....')
#         for s in sess_list:
#             prog = tv_recording(*s)
#             if prog.channel_id == channel_id and prog.start_ts == start_ts:
#                 selected_programs.append(prog)
#     template = loader.get_template('mythcontent/process_moves.html')
#     context = RequestContext(request, {'selected_programs': selected_programs, })
#     return HttpResponse(template.render(context))

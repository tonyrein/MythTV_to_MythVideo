from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

"""
Display a list of recorded TV programs
"""
def index(request):
    return HttpResponse("This page will display a list of TV programs.")

def videos(request):
    return HttpResponse("This page will display a list of videos.")
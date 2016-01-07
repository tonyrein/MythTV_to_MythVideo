from django.conf.urls import url

from . import views

urlpatterns = [
               url(r'^$', views.index, name='index'),
               url(r'^orphans/', views.orphans, name='orphans'),
               url(r'^play_file/(\d+)', views.play_file, name='play_file'),
#                url(r'^process_moves/', views.process_moves, name='process_moves'),
#                url(r'^videos/', views.videos, name='videos'),
               
]
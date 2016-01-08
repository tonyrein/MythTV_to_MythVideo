from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='mythcontent-index',),
    url(r'^process_moves', views.process_moves, name='mythcontent-process-moves',),
    url(r'^orphans/{0,1}$', views.orphans, name='mythcontent-orphans'),
    url(r'^orphan/edit/(\d+)', views.edit_orphan, name='mythcontent-edit-orphan',),
               
               
]

# 
# urlpatterns = [
#                url(r'^$', views.index, name='index'),
#                url(r'^orphans/', views.orphans, name='orphans'),
#                url(r'^play_file/(\d+)', views.edit_orphan, name='mythcontent-edit-orphan'),
# #                url(r'^process_moves/', views.process_moves, name='process_moves'),
# #                url(r'^videos/', views.videos, name='videos'),
#                
# ]
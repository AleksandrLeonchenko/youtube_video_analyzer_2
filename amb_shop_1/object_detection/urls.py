from django.urls import path

from .api import UploadingVideoFile, ListVideoFiles, DetailVideoFile, ProcessVideo

urlpatterns = [
    path('download_video/', UploadingVideoFile.as_view(), name='download_video'),
    path('video/', ListVideoFiles.as_view(), name='list_video'),
    path('video/<int:pk>', DetailVideoFile.as_view(), name='detail_video'),
    path('video/<int:pk>/start', ProcessVideo.as_view(), name='process_video'),

]

from django.urls import path
from .api import ClickHandler

urlpatterns = [
    path('click/', ClickHandler.as_view(), name='click_handler'),
]

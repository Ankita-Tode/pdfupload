from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("upload/", views.upload, name="upload"),
    path("chat/<int:session_id>/", views.chat_view, name="chat"),
    path("ask/<int:session_id>/", views.ask, name="ask"),
]

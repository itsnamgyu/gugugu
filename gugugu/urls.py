from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gu/ajax/validate-room-name', views.validate_room_name, name='validate_room_name'),
    path('<slug:name>', views.room, name='room'),
    path('gu/ajax/room/<int:pk>/ajax', views.room_ajax, name='room_ajax'),
]

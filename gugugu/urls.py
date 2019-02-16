from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gu/ajax/validate-room-name', views.validate_room_name, name='validate_room_name'),
    path('<slug:name>', views.room, name='room'),
    path('gu/ajax/room/<int:pk>', views.room_ajax, name='room_ajax'),
    path('gu/ajax/room/<int:room_id>/message/<int:message_id>', views.clap_ajax, name='clap_ajax'),
]

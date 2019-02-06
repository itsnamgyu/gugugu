from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gu/ajax/validate-room-name', views.validate_room_name, name='validate_room_name'),
    path('gu/create-room', views.create_room, name='create_room'),
    path('<slug:name>', views.room, name='room'),
]

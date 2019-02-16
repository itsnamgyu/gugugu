from django.urls import path
from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView, LogoutView, SignupView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gu/ajax/validate-room-name', views.validate_room_name, name='validate_room_name'),
    path('<slug:name>', views.room, name='room'),
    path('gu/ajax/room/<int:pk>', views.room_ajax, name='room_ajax'),

    # name field is used in allauth
    path('gu/login', LoginView.as_view(template_name='gugugu/login.html'), name='account_login'),
    path('gu/signup', SignupView.as_view(), name='account_signup'),
    path('gu/logout', LogoutView.as_view(), name='account_logout'),
]

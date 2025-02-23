from django.contrib import admin
from django.urls import include, path
from reservations.views import login_user, main_page, reserve_spot, unreserve_spot, logout_user, register_user

urlpatterns = [
    path('', login_user, name='login_user'),
    path('main', main_page, name='main_page'),
    path('logout/', logout_user, name='logout_user'),
    path('register/', register_user, name='register_user'),
    path('reserve/', reserve_spot, name='reserve'),
    path('unreserve/', unreserve_spot, name='unreserve'),
]

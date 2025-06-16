from django.urls import path
from reservations.views import  login_user, \
                                main_page, \
                                reserve_spot, \
                                unreserve_spot, \
                                logout_user, \
                                register_user, \
                                interest_queue, \
                                company, \
                                moderator, \
                                add_parking_spot, \
                                remove_user, \
                                remove_spot

urlpatterns = [
    path('', login_user, name='login_user'),
    path('main', main_page, name='main_page'),
    path('logout/', logout_user, name='logout_user'),
    path('register/', register_user, name='register_user'),
    path('reserve/', reserve_spot, name='reserve'),
    path('unreserve/', unreserve_spot, name='unreserve'),
    path('interest_queue', interest_queue, name='interest_queue'),
    path('company/<int:id>/', company, name='company'),
    path('company/<int:id>/admin/', moderator, name='moderator'),
    path('add_spot/<int:id>', add_parking_spot, name='add_spot'),
    path('remove_user/<int:id>', remove_user, name='remove_user'),
    path('remove_spot/<int:id>', remove_spot, name="remove_spot")
]

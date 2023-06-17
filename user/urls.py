from django.urls import path

from user.views import login_view
from django.contrib.auth.views import LogoutView

app_name = 'user'
urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
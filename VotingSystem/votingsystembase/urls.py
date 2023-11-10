from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('Request',views.Request, name="Request"),
    path('User_login', views.User_login, name="User_login"),
]



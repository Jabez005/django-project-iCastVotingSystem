from django.urls import path
from . import views

urlpatterns =[
    path('voter_login', views.voter_login, name="login_voter"),
    path('home', views.home, name="Home"),
]
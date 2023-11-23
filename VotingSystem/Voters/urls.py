from django.urls import path
from . import views

urlpatterns =[
    path('voter_login', views.voter_login, name="login_voter"),
    path('home', views.home, name="Home"),
    path('dynamic_form_view', views.dynamic_form_view, name="dynamic_form"),
]
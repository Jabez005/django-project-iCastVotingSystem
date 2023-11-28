from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns =[
    path('voter_login', views.voter_login, name="login_voter"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home', views.home, name="Home"),
    path('dynamic_form_view', views.dynamic_form_view, name="dynamic_form_view"),
    path('show_candidates', views.show_candidates, name="candidates"),
    path('Not_started', views.Not_started, name="Not_started"),
    path('Ended', views.Ended, name="Ended"),
    path('Results_not_open', views.Results_not_open, name="Results_not_open"),
    path('form_submitted', views.form_submitted, name="form_submitted"),
]
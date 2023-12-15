from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns =[
    path('login_superuser', views.login_superuser, name="login_superuser"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('Superadmin', views.Superadmin, name="Superadmin"),
    path('requests', views.requests, name="requests"),
    path('Requestform/<int:pk>', views.singular_request, name="view"),
    path('approve_request/<int:request_id>', views.approve_request, name = "approve_request"),
    path('reject_request/<int:request_id>', views.reject_request, name = "reject_request"),
    path('voting_admins', views.voting_admins, name="VotingAdmins"),
    path('generate_admin_account/<int:admin_id>', views.generate_admin_account, name="generate_admin_account"),
    path('manage_questions', views.manage_questions, name="Survey_questions"),
    path('vote/<int:survey_id>', views.vote, name="vote"),
]
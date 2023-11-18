from django.urls import path
from . import views


urlpatterns = [
    path('Adminlogin', views.Adminlogin, name="Adminlogin"),
    path('Votingadmin', views.Votingadmin, name="Votingadmin"),
    path('upload_csv', views.upload_csv, name="Upload_CSV"),
    path('display_csv_data', views.display_csv_data, name="Display_data"),
    path('ManagePositions', views.ManagePositions, name="ManagePositions"),
    path('add_position_view', views.add_position_view, name="add_position"),
    path('generate_voter_accounts/<int:upload_id>/', views.generate_voter_accounts, name="generate_voter_accounts"),
    path('ManageParty/<int:admin_id>', views.ManageParty, name="Manage_Partylist"),
    path('add_party/<int:admin_id>', views.add_party, name="add_party"),
]
    


from django.urls import path
from . import views


urlpatterns = [
    path('Adminlogin', views.Adminlogin, name="Adminlogin"),
    path('Votingadmin', views.Votingadmin, name="Votingadmin"),
    path('upload_csv', views.upload_csv, name="Upload_CSV"),
    path('display_csv_data', views.display_csv_data, name="Display_data"),
    path('ManagePositions', views.ManagePositions, name="ManagePositions"),
    path('add_position_view', views.add_position_view, name="add_position"),
    path('generate_voter_accounts', views.generate_voter_accounts, name="generate_voter_accounts"),
    path('ManageParty', views.ManageParty, name="ManageParty"),
    path('add_party', views.add_party, name="add_party"),
    path('field_list', views.field_list, name="field_list"),
    path('field_create', views.field_create, name="field_create"),
    path('field_update/<int:field_id>', views.field_update, name="field_update"),
    path('field_delete/<int:field_id>', views.field_delete, name="field_delete"), 
]
    


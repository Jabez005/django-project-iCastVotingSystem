from django.urls import path
from . import views


urlpatterns = [
    path('Adminlogin', views.Adminlogin, name="Adminlogin"),
    path('Votingadmin', views.Votingadmin, name="Votingadmin"),
    path('Voters', views.Voters, name="ManageVoters"),
    path('upload_csv', views.upload_csv, name="Upload_CSV"),
    path('display_csv_data', views.display_csv_data, name='Display_data'),
]
    


from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from VotingAdmin.models import VoterProfile

class VoterAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, org_code=None):
        try:
            user = User.objects.get(username=username)
            profile = VoterProfile.objects.get(user=user)
            if user.check_password(password) and profile.org_code == org_code:
                return user
        except User.DoesNotExist:
            pass  # Return None if user doesn't exist
        except VoterProfile.DoesNotExist:
            pass  # Return None if VoterProfile doesn't exist
        return None
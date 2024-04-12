"""
View pour le API utilisateur

"""
from rest_framework import generics, authentication, permissions

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system """
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Creer un auth token pour l'user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Manage api de l'utilisateur """
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """recuperer et returner  utilisateur authenticated """
        return self.request.user


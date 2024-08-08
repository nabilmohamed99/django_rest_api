"""
Views pour le module Machine Learning

"""
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Appariel, AppData, MLModel
from ml import serializers



class BaseMlAtrributeViewSet(mixins.DestroyModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """Base pour les vues de l'API ML"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

class ApparielViewSet(viewsets.ModelViewSet):
    """Gérer les appariels dans la base de données"""
    serializer_class = serializers.ApparielDetailSerializer
    queryset = Appariel.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Renvoyer les objets pour l'utilisateur connecté uniquement"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def get_serializer_class(self):
        """Renvoyer le serializer approprié en fonction de l'action"""
        if self.action == 'list':
            return serializers.ApparielSerializer


        return self.serializer_class

    def perform_create(self, serializer):
        """Creer un nouveau appariel"""
        serializer.save(user=self.request.user)


class AppDataView(BaseMlAtrributeViewSet):
    """Manager les AppData"""
    serializer_class =serializers.AppDataSerializer
    queryset = AppData.objects.all()


    def get_queryset(self):
        """Filtrer pour l'utilisateur authentifié"""
        return self.queryset.filter(appariel__user=self.request.user).order_by('-id')


class MLModelsViewSet(BaseMlAtrributeViewSet):
    """Gérer les modèles ML dans la base de données"""
    serializer_class = serializers.MLModelSerializer
    queryset = MLModel.objects.all()
 

    def get_queryset(self):
        """Renvoyer les objets pour l'utilisateur connecté uniquement"""
        return self.queryset.filter(appariel__user=self.request.user).order_by('-id')


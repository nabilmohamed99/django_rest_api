"""
Views pour le module Machine Learning

"""
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse


from core.models import Appariel, AppData, MLModel
from ml import serializers


class BaseMlAtrributeViewSet(mixins.DestroyModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.ListModelMixin,
                            mixins.CreateModelMixin,

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

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.MLModelSerializer
        elif self.action == 'upload_file':
            print("upload_file")
            return serializers.MlModelsFileSerializer

        return self.serializer_class

    @extend_schema(
        request=serializers.MLModelSerializer,
        responses={201: serializers.MLModelSerializer},
        description="Create a new ML model"
    )
    def create(self, request, *args, **kwargs):
        """Créer un nouveau modèle ML"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
    request=serializers.MlModelsFileSerializer,
    responses=serializers.MlModelsFileSerializer,
    description="Upload a file to a ML model"
    )
    @action(methods=['POST'], detail=True, url_path='mlmodel-upload-file')
    def upload_file(self, request, pk=None):
        """Upload un fichier à un modèle"""
        mlmodel = self.get_object()
        serializer = self.get_serializer(mlmodel, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

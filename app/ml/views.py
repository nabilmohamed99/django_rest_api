"""
Views pour le module Machine Learning

"""
from rest_framework import (
    viewsets,
    mixins,
)
import logging

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse,OpenApiExample

from django_filters import rest_framework as filters
import tensorflow as tf

from core.models import Appariel, AppData, MLModel
from ml import serializers
import keras
from keras.utils import custom_object_scope
from datetime import datetime, timedelta
import numpy as np
from django.conf import settings
import os
import pathlib

logger = logging.getLogger(__name__)



@keras.saving.register_keras_serializable(package="NBeatsBlock")
class NBeatsBlock(tf.keras.layers.Layer):
    def __init__(self, input_size, theta_size, horizon, n_neurons, n_layers, **kwargs):
        super().__init__(**kwargs)
        self.input_size = input_size
        self.theta_size = theta_size
        self.horizon = horizon
        self.n_neurons = n_neurons
        self.n_layers = n_layers

        self.hidden = [tf.keras.layers.Dense(n_neurons, activation="relu") for _ in range(n_layers)]
        self.theta_layer = tf.keras.layers.Dense(theta_size, activation="linear", name="theta")

    def call(self, inputs):
        x = inputs
        for layer in self.hidden:
            x = layer(x)
        theta = self.theta_layer(x)
        backcast, forecast = theta[:, :self.input_size], theta[:, -self.horizon:]
        return backcast, forecast

class BaseMlAtrributeViewSet(mixins.DestroyModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.ListModelMixin,
                            mixins.CreateModelMixin,

                             viewsets.GenericViewSet):
    """Base pour les vues de l'API ML"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class ApparielFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='exact')
    name_contains = filters.CharFilter(field_name='name', lookup_expr='icontains')

    user_id = filters.NumberFilter(field_name='user__id', lookup_expr='exact')
    user_name = filters.CharFilter(field_name='user__name', lookup_expr='icontains')
    user_email = filters.CharFilter(field_name='user__email', lookup_expr='icontains')




    class Meta:
        model = Appariel
        fields = ['name', 'name_contains', 'user_id', 'user_name', 'user_email']

class ApparielViewSet(viewsets.ModelViewSet):
    """Gérer les appariels dans la base de données"""
    serializer_class = serializers.ApparielDetailSerializer
    queryset = Appariel.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    filterset_class = ApparielFilter

    filterset_fields = {
    'name': ['exact', 'icontains', 'istartswith', 'iendswith'],
    'user__id': ['exact'],
    'user__username': ['icontains'],
    'user__email': ['icontains'],
    }

    search_fields = ('^name', 'description', 'user__name', 'user__email')

    ordering_fields = ('name', 'user__name', 'user__email', 'created_at', 'updated_at')

    ordering = ('name',)

    @extend_schema(
        parameters=[
            OpenApiParameter('name', OpenApiTypes.STR, description='Filter by name'),
            OpenApiParameter('name_contains', OpenApiTypes.STR, description='Filter by name containing string'),
            OpenApiParameter('user_id', OpenApiTypes.INT, description='Filter by user ID'),
            OpenApiParameter('user_name', OpenApiTypes.STR, description='Filter by user name'),
            OpenApiParameter('user_email', OpenApiTypes.STR, description='Filter by user email'),
        ],

    )
    def list(self, request, *args, **kwargs):
        """List all appariels"""
        return super().list(request, *args, **kwargs)

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



class PredictView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            'application/json': {
                'model_name': 'string',
                'data': [i for i in range(72)]
            }
        },
        responses=OpenApiResponse({
            'application/json': {
                'prediction': [i for i in range(24)]
            }
        }),
        examples=[
            OpenApiExample(
                'Example Request',
                value={'model_name': 'MyModel', 'data': [1, 2, 3]},
                request_only=True
            ),
            OpenApiExample(
                'Example Response',
                value={'prediction': [[0.1, 0.2, 0.3]]},
                response_only=True
            )
        ]
    )
    def post(self, request):
        model_name = request.data.get('model_name')
        data_to_predict = request.data.get('data')

        if not model_name or data_to_predict is None:
            logger.error("Missing model_name or data in the request")
            return Response({'error': 'Please provide both model_name and data.'}, status=status.HTTP_400_BAD_REQUEST)

        data_to_predict = np.array(data_to_predict).reshape(1, -1)

        try:
            ml_model = MLModel.objects.get(name=model_name)
        except MLModel.DoesNotExist:
            logger.error(f"Model with name '{model_name}' does not exist")
            return Response({'error': f"Le modèle avec le nom '{model_name}' n'existe pas."}, status=status.HTTP_404_NOT_FOUND)

        model_file_path = ml_model.model_file.path
        logger.info(f"Model file path: {model_file_path}")

        if not os.path.exists(model_file_path):
            logger.error(f"Model file not found at path: {model_file_path}")
            return Response({'error': f"Model file not found: {model_file_path}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            with custom_object_scope({'NBeatsBlock': NBeatsBlock}):
                model_loaded = load_ml_model(model_file_path)
                prediction = model_loaded.predict(data_to_predict)
                logger.info(f"Prediction: {prediction}")
        except Exception as e:
            logger.exception("Error during model prediction")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'prediction': prediction.tolist()})





def load_ml_model(model_filename):
    model_file_path = pathlib.Path(model_filename)
    if not model_file_path.exists():
        raise ValueError(f"File not found: filepath={model_file_path}")
    return tf.keras.models.load_model(str(model_file_path))

class GetDataView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    @extend_schema(
        parameters=[
            OpenApiParameter('param', str, OpenApiParameter.QUERY, description='Appareil identifier')
        ],
        responses={
            200: OpenApiResponse(description="Success response with data"),
            400: OpenApiResponse(description="Bad request error message")
        }
    )
    def get(self, request):
        param = request.query_params.get('param')
        cache_key = f"data_{param}"
        cached_data = cache.get(cache_key)
        appareils = {
        "TR1_2": "PM2.DG TR1_2.029_import_active_energie",
        "TR3": "PM1.DG TR3.029_import_active_energie",
        "TR5": "PM4.DG TR5.029_import_active_energie",
        "TR6": "PM3.DG TR6.029_import_active_energie"
        }
        var_name=appareils[param]
        print(var_name)
        if cached_data:
            return Response(cached_data)

        date_actuelle = datetime.now()
        date_actuelle = date_actuelle.replace(day=1)
        date_previeus = date_actuelle - timedelta(hours=72)
        date_actuelle_formatee = date_actuelle.strftime("%d%m%Y%H%M%S")
        date_previeus_formatee = date_previeus.strftime("%d%m%Y%H%M%S")
        url=f"http://192.168.1.128:80/services/user/records.xml/?begin={date_previeus_formatee}?end={date_actuelle_formatee}?period=3600?var="+var_name
        print(url)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print("ici")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        print(response.content)
        xml_data = response.content
        soup = BeautifulSoup(xml_data, 'xml')
        values = [float(field.find("value").text) for record in soup.find_all('record') for field in record.find_all("field")]

        cache.set(cache_key, values, timeout=3600)  # Cache pendant 1 heure
        return Response(values)

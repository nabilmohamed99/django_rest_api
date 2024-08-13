"""Test pour l'api de machine learning"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils.crypto import get_random_string

from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from core.models import MLModel, Appariel
from ml.serializers import MLModelSerializer
from django.utils.dateparse import parse_datetime
import os
from django.core.files.uploadedfile import SimpleUploadedFile

ML_MODEL_URL = reverse('ml:mlmodel-list')


def file_upload_url(mlmodel_id):
    """Create and retrun the file upload URL"""
    return reverse('ml:mlmodel-upload-file', args=[mlmodel_id])

def user_detail_url(user_id):
    """Return user detail URL"""
    return reverse('ml:mlmodel-detail', args=[user_id])
def create_user(email='user02@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)

def create_appariel(user, **params):
    defaults = {
        'name': f'appariel_{get_random_string(8)}',
        'description': 'Sample description',
    }
    defaults.update(params)
    return Appariel.objects.create(user=user, **defaults)

class PublicModelsApiTests(TestCase):
    """Test unauthenticated model API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(ML_MODEL_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateModelsApiTests(TestCase):
    """Test authenticated model API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@exemple.com', password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_ml_models(self):
        """Test retrieving a list of ML models"""
        appariel = create_appariel(user=self.user)
        MLModel.objects.create(
            appariel=appariel,
            name='model1',
            created_at=parse_datetime("2024-01-01T00:00:00Z"),
            updated_at=parse_datetime("2024-01-01T00:00:00Z"),
            model_file="C:\\WorkSpace\\LemoIA\\rest_api_ml\\restful_ml_api\\models\\model_nbeats_tr1_2_energie.keras"
        )
        MLModel.objects.create(
            appariel=appariel,
            name='model2',
            created_at=parse_datetime("2024-01-01T00:00:00Z"),
            updated_at=parse_datetime("2024-01-01T00:00:00Z"),
            model_file="C:\\WorkSpace\\LemoIA\\rest_api_ml\\restful_ml_api\\models\\model_nbeats_tr1_2_energie.keras"
        )

        res = self.client.get(ML_MODEL_URL)
        models = MLModel.objects.all().order_by('-name')
        serializer = MLModelSerializer(models, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['appariel'], serializer.data[0]['appariel'])



    def test_ml_models_limited_to_user(self):
        """Test that ml models for the authenticated user are returned"""
        user2 = create_user(email="user0001@example.com")
        self.client.force_authenticate(user2)
        appariel = create_appariel(user=user2)
        mlmodel=MLModel.objects.create(
            appariel=appariel,
            name='model1',
            created_at=parse_datetime("2024-01-01T00:00:00Z"),
            updated_at=parse_datetime("2024-01-01T00:00:00Z"),
            model_file="C:\\WorkSpace\\LemoIA\\rest_api_ml\\restful_ml_api\\models\\model_nbeats_tr1_2_energie.keras"
        )

        res = self.client.get(ML_MODEL_URL)
        models = MLModel.objects.filter(appariel__user=self.user).order_by('-name')

        serializer = MLModelSerializer(models, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], mlmodel.name)

    def test_update_ml_model(self):
        """Test updating a ML model"""
        appariel = create_appariel(user=self.user)
        mlmodel = MLModel.objects.create(
            appariel=appariel,
            name='model1',
            created_at=parse_datetime("2024-01-01T00:00:00Z"),
            updated_at=parse_datetime("2024-01-01T00:00:00Z"),
            model_file="C:\\WorkSpace\\LemoIA\\rest_api_ml\\restful_ml_api\\models\\model_nbeats_tr1_2_energie.keras"
        )

        payload = {
            'name': 'model2',
        }

        url = user_detail_url(mlmodel.pk)
        self.client.patch(url, payload)

        mlmodel.refresh_from_db()
        self.assertEqual(mlmodel.name, payload['name'])

    def test_delete_ml_model(self):
        """Test deleting a ML model"""
        appariel= create_appariel(user=self.user)
        mlmodel = MLModel.objects.create(
            appariel=appariel,
            name='model1',
            created_at=parse_datetime("2024-01-01T00:00:00Z"),
            updated_at=parse_datetime("2024-01-01T00:00:00Z"),
            model_file="C:\\WorkSpace\\LemoIA\\rest_api_ml\\restful_ml_api\\models\\model_nbeats_tr1_2_energie.keras"
        )
        url = user_detail_url(mlmodel.pk)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        model=MLModel.objects.filter(appariel__user=self.user)
        self.assertFalse(model.exists())

class FileUploadTests(TestCase):
    """Test file upload"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user00001@exemple.com",
            password="testpass123")
        self.client.force_authenticate(self.user)
        self.appariel = create_appariel(user=self.user)
        self.mlmodel = MLModel.objects.create(
            appariel=self.appariel,
            name='model1',
            created_at=parse_datetime("2024-01-01T00:00:00Z"),
            updated_at=parse_datetime("2024-01-01T00:00:00Z"),
            model_file="model_nbeats_tr1_2_energie.keras"
        )
    def tearDown(self):
        self.mlmodel.model_file.delete()

    def test_upload_file_to_mlmodel(self):
        """Test uploading a file to ML model"""
        url  = file_upload_url(self.mlmodel.pk)
        file = SimpleUploadedFile(
            name='test_model_file.keras',
            content=b'file_content',
            content_type='application/octet-stream'
        )
        res = self.client.post(url, {'model_file': file}, format='multipart')

        self.mlmodel.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('model_file', res.data)
        self.assertTrue(os.path.exists(self.mlmodel.model_file.path))
"""
Test pour appData API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
import json
from rest_framework import status
from rest_framework.test import APIClient
from django.utils.dateparse import parse_datetime

from core.models import AppData, Appariel
from ml.serializers import AppDataSerializer
from django.utils.crypto import get_random_string

APP_DATA_URL = reverse('ml:appdata-list')


def detail_url(appdata_id):
    """Return appdata detail URL"""
    return reverse('ml:appdata-detail', args=[appdata_id])


def create_user(email='user02@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)

def create_appariel(user, **params):
    defaults = {
        'name': f'appariel_{get_random_string(8)}',
        'description': 'Sample description',
    }
    defaults.update(params)

    return Appariel.objects.create(user=user, **defaults)

class PublicAppDataApiTests(TestCase):
    """Test unauthenticated appData API access"""

    def setUp(self):
        self.client = APIClient()


    def test_auth_required(self):
        res = self.client.get(APP_DATA_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateAppDataApiTests(TestCase):
    """Test authenticated appData API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_appdata(self):
        """Test retrieving a list of appData"""
        appariel = create_appariel(user=self.user)
        AppData.objects.create(
            appariel=appariel,
            data='{"data": "data"}',
            datetime=parse_datetime("2024-01-01T00:00:00Z")
        )

        res = self.client.get(APP_DATA_URL)

        appdata = AppData.objects.all().order_by('-id')
        serializer = AppDataSerializer(appdata, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_appdata_limited_to_user(self):
        """Test that appData for the authenticated user are returned"""
        user2 = create_user(email="user03@example.com")
        appariel = create_appariel(user=user2)
        app_data = AppData.objects.create(
            datetime=parse_datetime("2024-01-01T00:00:00Z"),
            appariel=appariel,
            data='{"data": "data"}',
        )

        res = self.client.get(APP_DATA_URL)
        self.assertEqual(len(res.data), 0)

        appariel_user1 = create_appariel(user=self.user)
        app_data_user1 = AppData.objects.create(
            datetime=parse_datetime("2024-01-01T00:00:00Z"),
            appariel=appariel_user1,
            data='{"data": "data"}',
        )

        res = self.client.get(APP_DATA_URL)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['data'], app_data_user1.data)
        self.assertEqual(res.data[0]["id"], app_data_user1.id)


    def test_update_appdata(self):
        """Test updating appData"""
        appariel = create_appariel(user=self.user)
        app_data = AppData.objects.create(
            datetime=parse_datetime("2024-01-01T00:00:00Z"),
            appariel=appariel,
            data='{"data": "data"}',
        )

        payload = {
        'data': '{"data": "updated data"}',
            }

        url = detail_url(app_data.id)
        res=self.client.patch(url, payload)

        app_data.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(app_data.data, json.loads(payload['data']))

    def test_delete_appdata(self):
        """Test deleting appData"""
        appariel = create_appariel(user=self.user)
        app_data = AppData.objects.create(
            datetime=parse_datetime("2024-03-01T00:00:00Z"),
            appariel=appariel,
            data='{"data": "data"}',
        )

        url = detail_url(app_data.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        app_data= AppData.objects.filter(id=app_data.id)
        self.assertFalse(app_data.exists())
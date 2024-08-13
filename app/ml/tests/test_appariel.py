"""
Tester l'api Ml
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import (
    Appariel,
    AppData
)
from ml.serializers import ApparielSerializer, ApparielDetailSerializer
from django.utils.crypto import get_random_string


APPARIEL_URL = reverse('ml:appariel-list')



def detail_url(appariel_id):
    """Return appariel detail URL"""
    return reverse('ml:appariel-detail', args=[appariel_id])

def create_appariel(user, **params):
    """Create and return a sample appariel"""
    defaults = {
        'name': f'appariel_{get_random_string(8)}',
        'description': 'Sample description',
    }
    defaults.update(params)

    return Appariel.objects.create(user=user, **defaults)


def create_user(**params):
    """Creer et retourner un nouveau utilisateur"""
    return get_user_model().objects.create_user(**params)

class PublicApparielApiTests(TestCase):
    """Test unaythenticated appariel API access"""

    def setUp(self):
        self.client = APIClient()



    def test_login_required(self):
        """test qui verifie que la connexion est requise pour acceder a l'api"""
        res = self.client.get(APPARIEL_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApparielApiTests(TestCase):
    """Test authenticated appariel API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user100@example.com",password="testpass123")
        self.client.force_authenticate(self.user)

    def test_retrieve_appariels(self):
        """Test retrieving a list of appariels"""
        create_appariel(user=self.user, name='test1', description='test')
        create_appariel(user=self.user, name='test2', description='test')

        res = self.client.get(APPARIEL_URL)


        appariels = Appariel.objects.all().order_by('-id')
        serializer = ApparielSerializer(appariels, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_appariels_limited_to_user(self):
        """Test that appariels for the authenticated utilisateur"""
        other_user = create_user(
            email='user21@exemple.com',
            password='testpasse'
        )
        create_appariel(user=other_user)
        create_appariel(user=self.user)
        res= self.client.get(APPARIEL_URL)

        appariels = Appariel.objects.filter(user=self.user)
        serializer = ApparielSerializer(appariels, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(serializer.data))

    def test_view_appariel_detail(self):
        """Test viewing a appariel detail"""
        appariel = create_appariel(user=self.user)

        url = detail_url(appariel.id)
        res = self.client.get(url)

        serializer = ApparielDetailSerializer(appariel)
        self.assertEqual(res.data, serializer.data)

    def test_create_appariel(self):
        """Test de creation d'un appariel"""
        payload = {
            'name': f'appariel_{get_random_string(8)}',
            'description': 'test description'
        }
        res = self.client.post(APPARIEL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        appariel= Appariel.objects.get(pk=res.data['pk'])
        for k, v in payload.items():
            self.assertEqual(v, getattr(appariel, k))

        self.assertEqual(appariel.user, self.user)

    def test_partial_update(self):
        """test un changement partiel"""
        original_description = 'original description'
        appariel= create_appariel(
            user=self.user,
            name='test',
            description=original_description
        )
        payload = {'description': 'new description'}
        url = detail_url(appariel.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        appariel.refresh_from_db()
        self.assertEqual(appariel.description, payload['description'])
        self.assertEqual(appariel.user, appariel.user)

    def test_full_update(self):
        """Test full update"""
        appariel= create_appariel(
            user=self.user,
            name='appariel2560',
            description='test description'
        )
        payload = {
            'name': 'new name',
            'description': 'new description'
        }
        url = detail_url(appariel.id)
        res= self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        appariel.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(v, getattr(appariel, k))

    def test_update_user_returns_error(self):
        """Test that updating the user returns an error"""
        new_user = create_user(email='user2@exemple.com',password='testpass123')
        appariel = create_appariel(user=self.user)
        payload = {'user': new_user.id}
        url = detail_url(appariel.id)
        self.client.put(url, payload)
        appariel.refresh_from_db()
        self.assertEqual(appariel.user, self.user)

    def test_delete_appariel(self):
        """Test deleting an appariel"""
        appariel= create_appariel(user=self.user)
        url = detail_url(appariel.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Appariel.objects.filter(pk=appariel.pk).exists())


    def test_create_appariel_with_new_data(self):
        """Test creating an appariel with new data"""
        payload = {
            'name': 'appariel_1',
            'description': 'test description',
            'app_data': [
                {'datetime': '2024-01-01T00:00:00Z', 'data': {'key': 'value1'}},
                {'datetime': '2024-01-02T00:00:00Z', 'data': {'key': 'value2'}}
            ]
        }
        res = self.client.post(APPARIEL_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        appariels = Appariel.objects.filter(user=self.user)
        self.assertEqual(len(appariels), 1)
        appariel = appariels[0]

        # Vérifiez les données associées
        app_data = AppData.objects.filter(appariel=appariel)
        print(app_data)
        self.assertEqual(app_data.count(), 2)
        for data in payload['app_data']:
            self.assertTrue(app_data.filter(data=data['data']).exists())

    def test_create_appariel_on_update(self):
        """Test creating an appariel with new data on update"""
        appariel = create_appariel(user=self.user)
        payload = {
            'app_data': [
                {'datetime': '2024-01-01T00:00:00Z', 'data': {'key': 'value1'}},
                {'datetime': '2024-01-02T00:00:00Z', 'data': {'key': 'value2'}}
            ]
        }
        url = detail_url(appariel.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        appariel.refresh_from_db()
        app_data = AppData.objects.filter(appariel=appariel)
        self.assertEqual(app_data.count(), 2)
        for data in payload['app_data']:
            self.assertTrue(app_data.filter(data=data['data']).exists())

    def test_filter_by_user_id(self):
        """Test filtering appariels by user ID"""
        create_appariel(user=self.user, name='User1 Appariel')
        other_user = create_user(email='other_user@example.com',name='User2 Appariel', password='testpass123')

        create_appariel(user=other_user, name='User2 Appariel')

        res = self.client.get(APPARIEL_URL, {'user_id': self.user.id})

        appariels = Appariel.objects.filter(user=self.user)
        serializer = ApparielSerializer(appariels, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_user_name(self):
        """Test filtering appariels by user name"""
        url = f'{reverse("ml:appariel-list")}?user_name={self.user.name}'
        res = self.client.get(url)
        appariels = Appariel.objects.filter(user__name__icontains=self.user.name)
        serializer = ApparielSerializer(appariels, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)








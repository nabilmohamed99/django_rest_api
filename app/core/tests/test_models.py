"""
Test for models
"""
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models
from django.utils.dateparse import parse_datetime

class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = "test@exemple.com"
        password = 'test@123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXEMPLE.com', 'test1@exemple.com'],
            ['Test2@Exemple.com', 'Test2@exemple.com'],
            ['TEST3@EXEMPLE.com', 'TEST3@exemple.com'],
            ['test4@exemple.com', 'test4@exemple.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testmail')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'

        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_appariel(self):
        """Test creating a appariel."""
        user = get_user_model().objects.create_user(
            'test@exemple.com',
            'testpass123'
        )
        model=models.Appariel.objects.create(

            user=user,
            name='tr6',

            description='tr6'
        )
        self.assertEqual(str(model), model.name)

    def test_create_appariel(self):
        """Test creating a appariel."""
        user = get_user_model().objects.create_user(
            'test78@example.com',
            'testpass123'
        )

        appariel = models.Appariel.objects.create(
            user=user,
            name='tr6',
            description='tr6'
        )

        test_datetime = parse_datetime("2024-01-01T00:00:00Z")

        model = models.AppData.objects.create(
            data={"test": "test"},
            datetime=test_datetime,
            appariel=appariel
        )

        self.assertEqual(model.appariel, appariel)
        self.assertEqual(model.data, {"test": "test"})
        self.assertEqual(model.datetime, test_datetime)

    def test_create_MLModel(self):
        """Test creating a MLModel."""
        appariel = models.Appariel.objects.create(
            user=get_user_model().objects.create_user(
                email="user@exemple.com",
                password="test123"
            ),
            name="tr6",
            description="tr6"
        )
        ml_model=models.MLModel.objects.create(
            appariel=appariel,
            name="model1",



            created_at=parse_datetime("2024-01-01T00:00:00Z"),
            updated_at=parse_datetime("2024-01-01T00:00:00Z"),
            model_file="C:\\WorkSpace\LemoIA\\rest_api_ml\\restful_ml_api\\models\\model_nbeats_tr1_2_energie.keras"
        )
    @patch('core.models.uuid.uuid4')
    def test_mlmodel_file_name_uuid(self, mock_uuid):
        """Test generating a file path """
        uuid="test-uuid"
        mock_uuid.return_value=uuid
        file_path=models.ml_model_upload_path(None,'myfile.keras')


    def tearDown(self):
        pass

        # self.appariel.delete()
        # self.user.delete()

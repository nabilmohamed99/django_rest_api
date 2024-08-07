"""
Test for models
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


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
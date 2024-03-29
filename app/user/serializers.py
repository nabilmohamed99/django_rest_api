"""
Serializers pour l'user Api View.
"""

from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serialzer poir l'objet utilisateur"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    """ override la methode create pour Apres ne pas sauvagarder le password
    en texte clear  la validation de donne"""
    def create(self, validated_data):
        """Create and retrun a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

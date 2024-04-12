"""
Serializers pour l'user Api View.
"""

from django.contrib.auth import (
    get_user_model,
    authenticate

)
from django.utils.translation import gettext as _

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

    def update(self, instance, validated_data):
        """update et returner l'utilisateur"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer pour l'utilisateur auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        # le type hidden
        style={'input_type': 'password'},
        # trim the input  space on the last of input
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Valider l'authentification de l'utilisateur"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            # request context contient des objets
            # comme le header de message https
            request=self.context.get('request'),
            username=email,
            password=password,

        )
        if not user:
            msg = _('ON peut pas se connecter avec ces credentials')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs
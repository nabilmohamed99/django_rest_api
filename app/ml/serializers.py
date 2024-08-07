"""
Serializers for the ml
"""

from rest_framework import serializers

from core.models import Appariel

class ApparielSerializer(serializers.ModelSerializer):


    class Meta:
        model = Appariel
        fields = ['pk', 'name','user']
        read_only_fields = ['pk', 'user']

class ApparielDetailSerializer(ApparielSerializer):
    """Serializer pour appariel detail"""

    class Meta(ApparielSerializer.Meta):
        fields = ApparielSerializer.Meta.fields + ['description']





"""
Serializers for the ml
"""

from rest_framework import serializers

from core.models import Appariel,AppData


class AppDataSerializer(serializers.ModelSerializer):
    """Serializer pour AppData"""

    class Meta:
        model=AppData
        fields= ["id","data",'datetime']
        read_only_fields=['id']



class ApparielSerializer(serializers.ModelSerializer):

    app_data = AppDataSerializer(many=True,source='appdata_set',required=False)

    class Meta:
        model = Appariel
        fields = ['pk', 'name','user','app_data']
        read_only_fields = ['pk', 'user','app_data']


    def create(self, validated_data):
        app_data_data = validated_data.pop('appdata_set', [])
        appariel = Appariel.objects.create(**validated_data)

        for app_data in app_data_data:
            AppData.objects.create(appariel=appariel, **app_data)
        return appariel

class ApparielDetailSerializer(ApparielSerializer):
    """Serializer pour appariel detail"""

    class Meta(ApparielSerializer.Meta):
        fields = ApparielSerializer.Meta.fields + ['description']




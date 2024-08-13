"""
Serializers for the ml
"""

from rest_framework import serializers

from core.models import Appariel,AppData,MLModel



class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = ['pk', 'name', 'appariel']
        read_only_fields = ['pk', 'appariel']

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

    def update(self, instance, validated_data):
        """update an appariel"""
        app_data_data = validated_data.pop('appdata_set', None)

        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance.save()
        if app_data_data is not None:
            AppData.objects.filter(appariel=instance).delete()
            for app_data in app_data_data:
                AppData.objects.create(appariel=instance, **app_data)
        return instance


class ApparielDetailSerializer(ApparielSerializer):
    """Serializer pour appariel detail"""

    class Meta(ApparielSerializer.Meta):
        fields = ApparielSerializer.Meta.fields + ['description']


class MlModelsFileSerializer(serializers.ModelSerializer):
   """Serializer for uploading files to ml models"""
   class Meta:
        model=MLModel
        fields=['id','model_file']
        read_only_fields=['id']
        extra_kwargs = {
            'model_file': { 'required': True}
        }

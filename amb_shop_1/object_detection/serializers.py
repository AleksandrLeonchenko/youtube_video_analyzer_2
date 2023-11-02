from rest_framework import serializers
from .models import ProcessedFiles, SourceVideoFiles


class UploadingVideoFileSerializer(serializers.ModelSerializer):
    # file_name = serializers.FileField()

    class Meta:
        model = SourceVideoFiles
        fields = (
            'file_name',
            'video_file',
        )


class VideoFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceVideoFiles
        fields = (
            'id',
            'file_name',
            'video_file',
            'date_of_download',
            'processed'
        )


class ObjectLabelsSerializer(serializers.Serializer):
    object_labels = serializers.DictField(child=serializers.CharField())

    # def create(self, validated_data):
    #     return validated_data.get('object_labels')
    #
    # def update(self, instance, validated_data):
    #     instance.update(validated_data.get('object_labels', instance))
    #     return instance


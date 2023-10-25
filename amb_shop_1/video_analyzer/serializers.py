from rest_framework import serializers
from .models import UserFiles


class UserFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFiles
        # fields = '__all__'
        fields = (
            'id',
            'user_id',
            'user_ip',
            'video_id',
            'file_path',
        )

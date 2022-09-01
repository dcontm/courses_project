from rest_framework import serializers
from django.contrib.auth import get_user_model



USER = get_user_model()


class PasswordResetSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)

    def validate (self, data):
        super().validate(data)
        try:
            USER.objects.get(email=data['email'])
        except:
            raise serializers.ValidationError('Пользователя с данным email не существует.')
        return data


class PasswordResetVerifySerializer(serializers.Serializer):

    password = serializers.CharField(required=True)
from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Profile
from .exceptions import EmailAlreadyUsed

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=52)
    password = serializers.CharField(max_length=128)

    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['email']


class UserRegSerializer(serializers.Serializer):
    fio = serializers.CharField(max_length=52)
    email = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128)

    def save(self, validated_data):
        try:
            user = User.objects.create_user(
                username=validated_data['email'],
                email=validated_data['email'],
                password=validated_data['password'],
            )
        except IntegrityError:
            raise EmailAlreadyUsed()
        try:
            Profile.objects.create(
                user=user,
                fio=validated_data['fio'],
                email=validated_data['email']
            )
        except IntegrityError:
            user.delete() 
            raise EmailAlreadyUsed()
        except Exception as e:
            user.delete()
            raise ValidationError(str(e))

        return user

    class Meta:
        fields = ['fio', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'fio', 'email', 'phone']
        extra_kwargs = {
            'fio': {'allow_blank': True},
            'phone': {'allow_blank': True}
        }

    def validate(self, data):
        profile = self.instance
        for field in data:
            if data[field] == '':
                data[field] = getattr(profile, field)
        return data

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        
        if not user.check_password(attrs['current_password']):
            raise ValidationError('Current password is incorrect!')

        if attrs['new_password'] != attrs['confirm_password']:
            raise ValidationError('New password didnt match with confirm password')

        if attrs['current_password'] == attrs['new_password'] == attrs['confirm_password']:
            raise ValidationError('New password should not be the same as current password')

        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
from rest_framework import serializers

__author__ = 'yuehaitao'


class User(object):
    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password


class UpdatePassword(User):
    def __init__(self, method):
        super(UpdatePassword, self).__init__()
        self.method = method


class UserSerializer(serializers.Serializer):
    user_name = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=100)

    def create(self, validated_data):
        return User(**validated_data)

    def update(self, instance, validated_data):
        instance.user_name = validated_data.get('user_name', instance.user_name)
        instance.password = validated_data.get('password', instance.password)
        return instance


class UpdatePasswordSerializer(serializers.Serializer):
    user_name = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=100)
    method = serializers.CharField(max_length=100)

    def create(self, validated_data):
        return UpdatePassword(**validated_data)

    def update(self, instance, validated_data):
        instance.user_name = validated_data.get('user_name', instance.user_name)
        instance.password = validated_data.get('password', instance.password)
        instance.method = validated_data.get('method', instance.method)
        return instance

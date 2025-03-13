from rest_framework import serializers
from app.models.player import Player

class PlayerRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    date_of_birth = serializers.DateField(required=False)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")

        # Check if username already exists
        if Player.nodes.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")

        # Check if email already exists
        if Player.nodes.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")

        return data

    def create(self, validated_data):
        # Remove confirm_password from the data
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        # Create the player
        return Player.create(password=password, **validated_data)

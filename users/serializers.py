from .models import User, WebProvider
from rest_framework import serializers

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            password = validated_data['password']
        )
        return user
    
class MiniUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email','user_name','profile')
        
class EmailFindSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=64, required=True)
    
class WebProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebProvider
        fields = ('id', 'user', 'provider_type', 'provider_id')

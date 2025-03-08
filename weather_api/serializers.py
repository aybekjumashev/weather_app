from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import TgUser

class RegistrationationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = TgUser 
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'telegram_id')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Paroller sáykes keliwi kerek."})
        return data

    def create(self, validated_data):
        user = TgUser.objects.create( 
            username=validated_data['username'],
            email=validated_data.get('email', None),
            first_name=validated_data.get('first_name', None),
            last_name=validated_data.get('last_name', None),
            telegram_id=validated_data.get('telegram_id', None) 
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(TokenObtainPairSerializer):
    user_details = serializers.SerializerMethodField() 

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['telegram_id'] = getattr(user, 'telegram_id', None)
        return token

    def get_user_details(self, obj): 
        user = self.user  
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'telegram_id': user.telegram_id,
            'city': user.city,
        }

    def validate(self, attrs):
        data = super().validate(attrs) 
        data['user_data'] = self.get_user_details(None)  
        return data
    


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgUser
        fields = ('first_name', 'last_name', 'email', 'city')




class WeatherSerializer(serializers.Serializer):
    city = serializers.CharField()
    temp = serializers.FloatField()
    desc = serializers.CharField()
    humidity = serializers.IntegerField()
    speed = serializers.FloatField()





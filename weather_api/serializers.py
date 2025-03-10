from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from .city_corrector import CityCorrector

class RegistrationationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User 
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Paroller sáykes keliwi kerek."})
        return data

    def create(self, validated_data):
        user = User.objects.create( 
            username=validated_data['username'],
            email=validated_data.get('email', None),
            first_name=validated_data.get('first_name', None),
            last_name=validated_data.get('last_name', None) 
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(TokenObtainPairSerializer):
    user_details = serializers.SerializerMethodField() 

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def get_user_details(self, obj): 
        user = self.user  
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'city': user.city,
            'latitude': user.latitude,
            'longitude': user.longitude,
        }

    def validate(self, attrs):
        data = super().validate(attrs) 
        data['user_data'] = self.get_user_details(None)  
        return data
    


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'city', 'latitude', 'longitude')
    
    def validate(self, data):
        city = data.get('city')
        if city:
            corrector = CityCorrector()
            corrected_city, lat, lon = corrector.correct_city_name(city)
            if corrected_city:
                data['city'] = corrected_city
                data['latitude'] = lat
                data['longitude'] = lon
            else:
                raise serializers.ValidationError({"city": "Qala atı durıs kiritilmegen."})
        return data




class WeatherSerializer(serializers.Serializer):
    city = serializers.CharField()
    temp = serializers.FloatField()
    desc = serializers.CharField()
    humidity = serializers.IntegerField()
    speed = serializers.FloatField()





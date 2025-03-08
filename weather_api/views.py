from rest_framework import generics, permissions
from .serializers import RegistrationationSerializer, LoginSerializer, UserUpdateSerializer, WeatherSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import NotFound
from .models import TgUser
from rest_framework.response import Response
from .utils import get_weather_data

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegistrationationSerializer
    permission_classes = [permissions.AllowAny]

class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            user = self.request.user
            return user
        except TgUser.DoesNotExist:
            raise NotFound("User tabılmadı.")

class WeatherAPIView(generics.GenericAPIView):
    serializer_class = WeatherSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, city):
        weather_data = get_weather_data(city)
        if weather_data:
            serializer = self.get_serializer(data=weather_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "Hawa rayı maǵlıwmatları tabılmadı."}, status=404)
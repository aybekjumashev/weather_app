from rest_framework import generics, permissions, status
from .serializers import RegistrationationSerializer, LoginSerializer, UserUpdateSerializer, WeatherSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import NotFound
from .models import User
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
        return self.request.user  # To'g'ridan-to'g'ri murojaat qilish

class WeatherAPIView(generics.GenericAPIView):
    serializer_class = WeatherSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, city):
        weather_data = get_weather_data(
            city,
            request.user.latitude,
            request.user.longitude,
            skip_correction=(request.user.city == city), # Qisqartirilgan shart
        )

        if weather_data:
            serializer = self.get_serializer(data=weather_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "Hawa rayı maǵlıwmatları tabılmadı."},
                status=status.HTTP_404_NOT_FOUND,
            )
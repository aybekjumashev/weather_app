from django.urls import path, include
from .views import RegisterAPIView, LoginAPIView, UserUpdateAPIView, WeatherAPIView

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('users/city/', UserUpdateAPIView.as_view(), name='city'), 
    path('weather/<str:city>/', WeatherAPIView.as_view(), name='weather')
]


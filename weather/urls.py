from django.urls import path

from .views import weather_forecast

app_name = "weather"


urlpatterns = [
    path("weather-forecast/", weather_forecast, name="weather-forecast"),
]

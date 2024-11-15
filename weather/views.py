from django.shortcuts import render
from django.shortcuts import redirect
from datetime import datetime
import requests

def weather_forecast(request):
    if request.method == 'GET' and 'q' in request.GET:
        city_name = request.GET.get('q')
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city_name}?unitGroup=metric&key=Z9WKQT48NZFKQSPCRKQCQX454&contentType=json"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            city_name = data.get('resolvedAddress', '')
            date = data.get('days', [{}])[0].get('datetime', '')
            temp = data.get('days', [{}])[0].get('temp', '')
            feelslike = data.get('days', [{}])[0].get('feelslike', '')

            date_formatted = datetime.strptime(date, '%Y-%m-%d')
            date = date_formatted.strftime('%d.%m.%Y')
            weekday = date_formatted.strftime('%A')

            weather_data = []
            for day in data["days"]:
                weather_description = day["description"].lower()
                icon_class = ""
                weather_condition = ""

                if "partly cloudy" in weather_description:
                    icon_class = "fas fa-cloud-sun"
                    weather_condition = "Partly cloudy"
                elif "cloudy" in weather_description:
                    icon_class = "fas fa-cloud"
                    weather_condition = "Cloudy"
                elif "clear" in weather_description:
                    icon_class = "fas fa-sun"
                    weather_condition = "Clear"
                elif "rain" in weather_description:
                    icon_class = "fas fa-cloud-showers-heavy"
                    weather_condition = "Rain"
                else:
                    icon_class = "fas fa-question"
                    weather_condition = "Unknown"

                weather_day = {
                    "humidity": day['humidity'],
                    "date": day["datetime"],
                    "temp_max": day["tempmax"],
                    "temp_min": day["tempmin"],
                    "snowdepth": day["snowdepth"],
                    "description": day["description"],
                    "icon_class": icon_class,
                    "weather_condition": weather_condition,
                }
                weather_data.append(weather_day)

                context = {
                    'weather_data': weather_data,
                    'city_name': city_name,
                    'date': date,
                    'weekday': weekday,
                    'temp':temp,
                    'feelslike': feelslike
                }

            return render(request, 'weather/weather-forecast.html', context)
        else:
            return redirect('weather:weather_forecast')
    else:
        return render(request, 'weather/weather-forecast.html')

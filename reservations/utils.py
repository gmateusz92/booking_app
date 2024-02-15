from calendar import HTMLCalendar
from .models import Booking
# from datetime import datetime, date

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, apartment=None):
        self.year = year
        self.month = month
        self.apartment = apartment
        super(Calendar, self).__init__()

    def formatday(self, day, bookings):
        booking_per_day = bookings.filter(check_in__day__lte=day, check_out__day__gte=day)

        d = ''
        for booking in booking_per_day:
            d += f'<div class="reservation"></div>'

        if day != 0:
            cell_style = 'background-color: red;' if booking_per_day else ''  # Dodaj styl dla całej komórki
            return f"<td class='calendar-cell' style='{cell_style}'><span class='date'>{day}  </span><ul> {d} </ul></td>"
        return '<td class="calendar-cell"></td>'

    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        bookings = Booking.objects.filter(name=self.apartment, check_in__year=self.year, check_out__month=self.month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, bookings)}\n'
        return cal


# def get_date(req_day):
#         if req_day:
#             year, month = (int(x) for x in req_day.split('-'))
#             return date(year, month, day=1)
#         return datetime.today() 

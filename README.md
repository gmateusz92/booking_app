## VacaHome
This code represents a Django application that manages reservations for apartments, similar to platforms like Booking.com or Airbnb. Here's a brief overview of the functionalities

## Key Features:
User Registration and Activation: Users can sign up and activate their account via an email link.
Login/Logout: Users can log in with credentials and log out from the application.
Profile Management: Users can update their personal profile details.
Password Recovery: Users can reset their password via a link sent to their email.
Search & Filters: Users can search apartments by location, sort by price, and check availability.

Booking System: Users can make reservations, check their bookings, and receive notifications. The user can select a place and set a radius in kilometers, when someone adds an apartment within a specific radius, he receives a notification about a new apartment.
User can check current bookings and send message to vendor (then vendor receive an email), can check booking history. After journey user can rate the apartment.

Owner Management: Hosts can manage their own listings and view bookings for their apartments. Host can send message to customer and delete reservation.
Users of app can also check weather all over the world.

## Technologies used:

PostgreSQL
GDAL
Google Search API
JavaScript and AJAX
Email System
Weather API




















This code represents a Django application that manages reservations for apartments, similar to platforms like Booking.com or Airbnb. Here's a brief overview of the functionalities:

Home Page (home):

Displays a list of apartments based on search queries for country or city.
Apartments are sorted by price, and average ratings are calculated for each apartment.
It also fetches weather data for the queried location and displays it.
Apartment Detail View (ApartmentDetailView):

Displays details about a specific apartment, including images and basic information.
The view supports navigating through calendar months, though calendar functionality is commented out in the code.
Add, Edit, and Delete Apartments:

AddApartmentView: Allows users to add a new apartment with details and images.
EditApartmentView: Allows users to edit an existing apartment’s details and manage its photos.
DeleteApartmentView: Enables users to delete an apartment listing.
Apartment Listing for Users (apartment_list):

Lists all the apartments owned by the logged-in user.
Booking Management:

Booking View (BookingView): Allows users to book apartments. It checks for overlapping bookings and ensures the requested dates are available.
Booking List (booking_list): Displays upcoming bookings for the logged-in user.
Vendor Booking List (vendor_booking_list): Shows bookings for apartments owned by the logged-in user.
Delete Booking (DeleteBookingView): Allows users to delete a booking.
Messaging (message_view):

Allows users to send messages between hosts and guests related to specific bookings.
Messages are emailed to the recipient with a template for notification.
Booking History:

Displays past bookings for the logged-in user. Users can leave comments and ratings for their stays.
Notification Preferences (AddNotificationPreferenceView, DeletePreferenceView):

Users can set notification preferences to receive alerts for different activities related to their apartments or bookings.
Reviews/Opinions (read_opinions):

Users can read comments and ratings left by other guests for an apartment.
Email Integration:

Several email notifications are integrated, such as reservation confirmations, new messages, and booking-related emails.
Calendar (commented out):

Intended functionality to display a calendar for checking apartment availability based on a given month, which integrates with booking dates.



Search & Filters: Users can search apartments by location, sort by price, and check availability.
User Accounts & Authentication: Features like registration, login/logout, and profile management are implemented.
Booking System: Users can make reservations, check their bookings, and receive notifications.
Owner Management: Hosts can manage their own listings and view bookings for their apartments.



Overview of the Functionality:
User Input: The user submits a search query with the city name via a GET request (e.g., through a form submission).
Weather API: The view makes a request to the VisualCrossing weather API to fetch the forecast data for the given city.
Data Processing: The data returned by the API is processed to extract weather details such as temperature, humidity, description, and icons.
Weather Icons: Based on the description of the weather (e.g., "partly cloudy", "clear", etc.), different FontAwesome icons are assigned to the weather condition.
Context for Rendering: The weather data is stored in a context dictionary and passed to a template (weather/weather-forecast.html) for rendering.
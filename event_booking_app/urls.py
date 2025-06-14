from django.urls import path
from .views import *


urlpatterns = [
   # path('event/', EventAPIView.as_view(),name='event'),
   # path('event/<int:pk>/', EventAPIView.as_view(),name='event-pk'),
   
   path('register/', RegisterAPIView.as_view(),name='register'),
   path('login/', LoginAPIView.as_view(),name='login'),

   path('event/<int:pk>/', EventView.as_view(), name='event-pk'),
   path('event/', EventView.as_view(), name='event'),
   path('events/', event_list_view, name='event-list'),

   path('book/', BookingCreateView.as_view(), name='book'),    #Handles API requests (JSON) using BookingSerializer
   path('book/event/<int:event_id>/', booking_form_view, name='booking-form'),    #Handles normal HTML form submission using Django templates
   
   path('logout/', logout_view, name='logout'),


   path('book/<int:booking_id>/qr/', TicketQRView.as_view()),     #no need to use this, its just to show qr
   path('qr-book/', QRBookingCreateView.as_view(), name='qr-booking'),
]
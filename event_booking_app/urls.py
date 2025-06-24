from django.urls import path
from . import views
from .views import *
from django.views.generic import RedirectView
from django.shortcuts import redirect


urlpatterns = [
   # path('event/', EventAPIView.as_view(),name='event'),
   # path('event/<int:pk>/', EventAPIView.as_view(),name='event-pk'),
   
   path('', LoginAPIView.as_view(), name='login'), 
   
   path('register/', RegisterAPIView.as_view(),name='register'),
   path('login/', LoginAPIView.as_view(),name='login'),

   path('event/<int:pk>/', EventView.as_view(), name='event-pk'),
   path('event/', EventView.as_view(), name='event'),
   path('events/', event_list_view, name='event-list'),

   path('book/', BookingCreateView.as_view(), name='book'),    #Handles API requests (JSON) using BookingSerializer
   path('book/event/<int:event_id>/', booking_form_view, name='booking-form'),    #Handles normal HTML form submission using Django templates
   
   path('logout/', logout_view, name='logout'),


   path('book/<int:booking_id>/qr/', TicketQRView.as_view()),     #no need to use this, its just to show qr
   path('qr-book/', QRBookingCreateView.as_view(), name='qr-book'),


   path('admin-login/', admin_login_view, name='admin-login'),
    path('admin-panel/', admin_dashboard_view, name='admin-dashboard'),
   
    path('admin-events/', admin_event_list_view, name='admin-event-list'),
    path('admin-events/add/', admin_add_event_view, name='admin-add-event'),
    path('admin-events/edit/<int:pk>/', admin_edit_event_view, name='admin-edit-event'),
    path('admin-events/delete/<int:pk>/', admin_delete_event_view, name='admin-delete-event'),
    path('admin-events/view/<int:pk>/', admin_view_event_view, name='admin-view-event'),


    path('admin-registered-users/', admin_registered_users_view, name='admin-registered-users'),
    path('admin-qr-bookings/', admin_qr_bookings_view, name='admin-qr-bookings'),
    path('admin-registered-bookings/', admin_registered_bookings_view, name='admin-registered-bookings'),



]
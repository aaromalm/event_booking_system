from django.contrib import admin
from .models import Event, Booking, QRBooking

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'organizer')
    search_fields = ('name', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'seats_booked', 'booking_time')

@admin.register(QRBooking)
class QRBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'email', 'seats_booked', 'booking_time')

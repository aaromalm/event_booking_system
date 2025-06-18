from django.db import models
from django.contrib.auth.models import User

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


class Event(models.Model):
    DOMAIN_CHOICES = [
        ('technology', 'Technology'),
        ('art_culture', 'Art & Culture'),
        ('music', 'Music'),
        ('sports', 'Sports'),
        ('gaming', 'Gaming'),
        ('business', 'Business'),
        ('education', 'Education'),
        ('health_wellness', 'Health & Wellness'),
        ('food_drinks', 'Food & Drinks'),
        ('fashion', 'Fashion'),
        ('travel_adventure', 'Travel & Adventure'),
    ]
    event_id=models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=255)
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    organizer=models.CharField(max_length=50)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    domain = models.CharField(max_length=30, choices=DOMAIN_CHOICES, default="Other")

    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    seats_booked = models.PositiveIntegerField()
    booking_time = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='booking_qr/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to get an ID

        qr_content = f"Booking by {self.user.username} for event '{self.event.name}' on {self.booking_time}"
        qr_img = qrcode.make(qr_content)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        filename = f'booking_{self.id}.png'

        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        super().save(update_fields=['qr_code'])

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"



class QRBooking(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    seats_booked = models.PositiveIntegerField()
    booking_time = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='booking_qr/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        qr_content = f"QR Booking by {self.name} for '{self.event.name}' on {self.booking_time}"
        qr_img = qrcode.make(qr_content)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        filename = f'qrbooking_{self.id}.png'

        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        super().save(update_fields=['qr_code'])

    def __str__(self):
        return f"{self.name} - {self.event.name}"
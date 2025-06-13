from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"

class QRBooking(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    seats_booked = models.PositiveIntegerField()
    booking_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.event.name}"

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model= Event
        fields='__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','username','password','confirm_password',]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        
        refresh = RefreshToken.for_user(user)
        data['user'] = user
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user', 'event', 'seats_booked', 'booking_time']
        read_only_fields = ['id', 'booking_time', 'user']

    def validate(self, data):
        event = data['event']
        seats_requested = data['seats_booked']

        if seats_requested <= 0:
            raise serializers.ValidationError("Seats booked must be greater than zero.")

        if event.available_seats < seats_requested:
            raise serializers.ValidationError(f"Only {event.available_seats} seats are available.")
        
        return data

    def create(self, validated_data):
        event = validated_data['event']
        seats_requested = validated_data['seats_booked']

        event.available_seats -= seats_requested
        event.save()

        booking = Booking.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        return booking
    
class QRBookingSerializer(serializers.ModelSerializer):
    event = serializers.SlugRelatedField(
        slug_field='name',                      #Tells the serializer to use Event.name as the identifier.
        queryset=Event.objects.all()
    )

    class Meta:
        model = QRBooking
        fields = ['id', 'name', 'email', 'event', 'seats_booked', 'booking_time']
        read_only_fields = ['id', 'booking_time']

    def validate(self,data):
        event= data['event']
        seats_requested= data['seats_booked']

        if seats_requested<= 0:
            raise serializers.ValidationError("Seats booked must be greater than zero.")
        if event.available_seats < seats_requested:
            raise serializers.ValidationError(f"Only {event.available_seats} seats are available.")

        return data

    def create(self, validated_data):
        event = validated_data['event']
        seats_requested = validated_data['seats_booked']

        # Update available seats
        event.available_seats -= seats_requested
        event.save()

        # Create QRBooking instance
        return QRBooking.objects.create(**validated_data)

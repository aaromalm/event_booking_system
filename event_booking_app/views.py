from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404

#for sending mail
from django.core.mail import send_mail,EmailMessage
from django.conf import settings

#for qr code
from django.http import HttpResponse
from .utils import generate_qr_code

#for template
from django.shortcuts import render,redirect

#for messages like "Registration Successfull"
from django.contrib import messages

#for logging in 
from django.contrib.auth import login  

def send_booking_email(to_email, event_name, seats, booking):
        subject = f"Booking Confirmation for {event_name}"
        message = f"Thank you for booking {seats} seats for {event_name}."
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email]
    )
        
        # Determine username or name
        if hasattr(booking, 'user'):
            username = booking.user.username
        elif hasattr(booking, 'name'):
            username = booking.name
        else:
            username = "Guest"

        qr_data = f"Booking ID: {booking.id}\nUser: {username}\nEvent: {event_name}\nSeats: {seats}\nDate: {booking.event.date}"
        qr_image = generate_qr_code(qr_data) 

        email.attach(f"ticket_qr_{booking.id}.png", qr_image, 'image/png')

        try:
            email.send()
            print("Email sent successfully!")
        except Exception as e:
            print("Error sending email:", e)


from django.views import View

class EventView(View):
    def get(self, request, pk=None):
        if pk:
            event = get_object_or_404(Event, pk=pk)
            return render(request, 'eventpk.html', {'event': event})
        events = Event.objects.all()
        return render(request, 'events.html', {'events': events})

"""
class EventAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            event = get_object_or_404(Event, pk=pk)
            return render(request, 'eventpk.html', {'event': event})
        
        events = Event.objects.all()
        return render(request, 'events.html', {'events': events})



    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # assumes authentication
            return Response({"message": "Event created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Event updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return Response({"message": "Event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
"""

class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')  # You can update the URL name as needed
        return render(request, 'register.html', {'errors': serializer.errors})



from django.contrib.auth import login

class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.POST)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            if user.is_staff:
                return redirect('/admin/') 

            login(request, user)
            
            return redirect('event')  

        return render(request, 'login.html', {'errors': serializer.errors})


        
        # API-based login (Postman, etc.)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({
                "message": "Login successful",
                "user": {
                    "username": user.username
                },
                "tokens": {
                    "refresh": serializer.validated_data['refresh'],
                    "access": serializer.validated_data['access']
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# BookingCreateView-- Handles API requests (JSON) using BookingSerializer

class BookingCreateView(APIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    


    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            booking = serializer.save()
 
            # Send confirmation email
            user_email = booking.user.email
            event_name = booking.event.name
            seats = booking.seats_booked
            send_booking_email(user_email, event_name, seats, booking)

            return Response(self.serializer_class(booking).data, status=status.HTTP_201_CREATED)
        return Response("Required No. of seats not available", status=status.HTTP_400_BAD_REQUEST)

# booking_form_view-- Handles normal HTML form submission using Django templates

# Form-based booking view ( Only allows logged-in users
#                           Validates seat availability
#                           Creates a booking
#                           Sends confirmation with QR
#                           Shows a success page)

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@login_required
def booking_form_view(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)

    if request.method == 'POST':
        seats = int(request.POST.get('seats'))

        if seats <= 0:
            messages.error(request, "Seats must be greater than zero.")
        elif event.available_seats < seats:
            messages.error(request, f"Only {event.available_seats} seats are available.")
        else:
            event.available_seats -= seats
            event.save()

            booking = Booking.objects.create(user=request.user, event=event, seats_booked=seats)
            send_booking_email(request.user.email, event.name, seats, booking)
            return render(request, 'booking_success.html', {'booking': booking})

    return render(request, 'booking_form.html', {'event': event})


# just to view the qr
class TicketQRView(APIView):
    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
            qr_data = f"Booking ID: {booking.id}\nUser: {booking.user.username}\nEvent: {booking.event.name}\nSeats: {booking.seats_booked}\nDate: {booking.event.date}"
            qr_image = generate_qr_code(qr_data)

            return HttpResponse(qr_image, content_type="image/png")

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)


class QRBookingCreateView(APIView):
    permission_classes=[permissions.AllowAny]

    def post(self,request):
        serializer= QRBookingSerializer(data=request.data)
        if serializer.is_valid():
            booking=serializer.save()

            # Send confirmation email
            user_email = booking.email
            event_name = booking.event.name
            seats = booking.seats_booked
            send_booking_email(user_email, event_name, seats, booking)

            return Response({
                "message": "Booking successful",
                "booking_id": booking.id
                },status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 # Generate the QR Code for booking without Logging in   
import qrcode

qr_url = "http://172.25.247.140:800/qr-book/"
qr = qrcode.make(qr_url)
qr.save("qr_booking_link.png")


# For logout
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')
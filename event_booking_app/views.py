from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404

#for sending mail
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
from .utils import generate_ticket_image 

#for qr code
from django.http import HttpResponse

#for template
from django.shortcuts import render,redirect

#for messages like "Registration Successfull"
from django.contrib import messages

#for logging in 
from django.contrib.auth import login  


def send_booking_email(to_email, event_name, seats, booking):
        
        if hasattr(booking, 'user'):
            username = booking.user.username
        elif hasattr(booking, 'name'):
            username = booking.name
        else:
            username = "Guest"
    
        subject = f"Booking Confirmation for {event_name}"
        message = f"Hi {username},\n\nThank you for booking {seats} seat(s) for '{event_name}'.\nPlease find your ticket attached below.\n\nEnjoy the event!\n\n- EventHive Team"
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email]
    )

        ticket_image = generate_ticket_image(booking)
        email.attach(f"EventHive_Ticket_{booking.id}.png", ticket_image, 'image/png')
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
            return redirect('login')  
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
                return redirect('admin-dashboard') 

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

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
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
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        events = Event.objects.all()
        return render(request, 'qr-book.html', {'events': events})

    def post(self, request):
        serializer = QRBookingSerializer(data=request.POST) 

        if serializer.is_valid():
            booking = serializer.save()

            user_email = booking.email
            event_name = booking.event.name
            seats = booking.seats_booked
            send_booking_email(user_email, event_name, seats, booking)

            messages.success(request, "Booking successful!")
            return redirect('qr-book')  # Redirect to same page or a 'thank you' page

        # If errors, render the form again with errors and events
        events = Event.objects.all()
        return render(request, 'qr-book.html', {
            'events': events,
            'errors': serializer.errors,
        })
    
 # Generate the QR Code for booking without Logging in   
import qrcode

qr_url = "http://172.25.247.140:8000/qr-book/"
qr = qrcode.make(qr_url)
qr.save("qr_booking_link.png")


# For logout
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

@require_POST
@csrf_protect
def logout_view(request):
    logout(request)
    return redirect('login')



#For filtering
from .models import Event

def event_list_view(request):
    events = Event.objects.all()

    location = request.GET.get('location')
    search_query = request.GET.get('q')  # for search bar in navbar

    if search_query:
        events = events.filter(name__icontains=search_query)

    if location:
        events = events.filter(location__icontains=location)

    return render(request, 'events.html', {
        'events': events,
        'search_query': search_query,
        'location': location,
    })


#admin view
from django.contrib.auth import authenticate
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .forms import EventForm


def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin-dashboard')
        else:
            messages.error(request, "Invalid admin credentials.")

    return render(request, 'admin_login.html')

@staff_member_required(login_url='/admin-login/')
def admin_dashboard_view(request):
    events = Event.objects.all()
    users = User.objects.filter(is_staff=False)
    qr_users = QRBooking.objects.all()
    total_registered_bookings = Booking.objects.count()
    return render(request, 'admin_dashboard.html', {
        'events': events,
        'users': users,
        'qr_users': qr_users,
        'total_registered_bookings': total_registered_bookings,
    })


@staff_member_required(login_url='/admin-login/')
def admin_registered_users_view(request):
    users = User.objects.filter(is_staff=False)
    return render(request, 'admin_registered_users.html', {'users': users})

@staff_member_required(login_url='/admin-login/')
def admin_qr_bookings_view(request):
    qr_users = QRBooking.objects.all()
    return render(request, 'admin_qr_bookings.html', {'qr_users': qr_users})

@staff_member_required(login_url='/admin-login/')
def admin_registered_bookings_view(request):
    bookings = Booking.objects.select_related('user', 'event')
    return render(request, 'admin_registered_bookings.html', {'bookings': bookings})

@staff_member_required
def admin_event_list_view(request):
    events = Event.objects.all().prefetch_related('booking_set')
    return render(request, 'admin_event_list.html', {'events': events})

@staff_member_required(login_url='/admin-login/')
def admin_add_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin-event-list')
    else:
        form = EventForm()
    return render(request, 'admin_add_event.html', {'form': form})

@staff_member_required(login_url='/admin-login/')
def admin_edit_event_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('admin-event-list')
    else:
        form = EventForm(instance=event)
    return render(request, 'admin_edit_event.html', {'form': form})

@staff_member_required(login_url='/admin-login/')
def admin_delete_event_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    return redirect('admin-event-list')

@staff_member_required(login_url='/admin-login/')
def admin_view_event_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    registered_bookings = Booking.objects.filter(event=event)
    qr_bookings = QRBooking.objects.filter(event=event)

    total_amount = sum(b.seats_booked * event.fees for b in registered_bookings) + sum(b.seats_booked * event.fees for b in qr_bookings)
    total_bookings = sum(b.seats_booked for b in registered_bookings) + sum(b.seats_booked for b in qr_bookings)
    return render(request, 'admin_view_event.html', {
        'event': event,
        'registered_bookings': registered_bookings,
        'qr_bookings': qr_bookings,
        'total_amount': total_amount,
        'total_bookings': total_bookings
    })

#Custom Admin login
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def create_admin_user(request):
    User = get_user_model()
    if not User.objects.filter(username='aaromal123').exists():
        User.objects.create_superuser(
            username='aaromal123',
            email='aaromalm1032004@gmail.com',
            password='aaromal123'
        )
        return HttpResponse("Custom superuser created successfully.")
    return HttpResponse("Admin already exists.")

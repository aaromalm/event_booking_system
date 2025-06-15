# utils.py
import qrcode
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

# def generate_qr_code(data: str):
#     qr = qrcode.QRCode(
#         version=1,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(data)
#     qr.make(fit=True)

#     img = qr.make_image(fill_color='black', back_color='white')

#     # Save to memory buffer
#     buffer = BytesIO()
#     img.save(buffer, format='PNG')
#     return buffer.getvalue()  

def generate_ticket_image(booking):
    event = booking.event

    # Determine user name
    if hasattr(booking, 'user') and booking.user:
        username = booking.user.username
    elif hasattr(booking, 'name'):
        username = booking.name
    else:
        username = "Guest"

    # QR data
    qr_data = f"Booking ID: {booking.id}\nUser: {username}\nEvent: {event.name}\nDate: {event.date}\nSeats: {booking.seats_booked}"
    qr = qrcode.make(qr_data).resize((200, 200))

    # Ticket dimensions
    width, height = 520, 800
    card = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(card)

    # Load fonts
    try:
        font_bold = ImageFont.truetype("arialbd.ttf", 24)
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font_bold = font = ImageFont.load_default()

    # 1. Event Image (Top)
    if hasattr(event, 'image') and event.image:
        try:
            event_img = Image.open(event.image.path).resize((480, 220))
            card.paste(event_img, (20, 20))
        except Exception as e:
            print("Failed to load event image:", e)

    # 2. Event Info
    y = 260
    x = 30
    line_spacing = 35
    draw.text((x, y), event.name, font=font_bold, fill="black")
    y += line_spacing
    draw.text((x, y), f"Date: {event.date.strftime('%a, %d %b | %I:%M %p')}", font=font, fill="black")
    y += line_spacing
    draw.text((x, y), f"Venue: {event.location}", font=font, fill="black")
    y += line_spacing
    draw.text((x, y), f"Booked by: {username}", font=font, fill="black")
    y += line_spacing
    draw.text((x, y), f"Seats: {booking.seats_booked}", font=font, fill="black")
    y += line_spacing
    draw.text((x, y), f"Booking ID: {booking.id}", font=font, fill="black")

    # 3. QR Code (Center)
    qr_x = (width - qr.width) // 2
    card.paste(qr, (qr_x, y + 50))

    # 4. Total Price Footer
    draw.rectangle([(0, height - 50), (width, height)], fill="#f0f0f0")
    total_text = f"Total Paid: ₹ {event.fees * booking.seats_booked:.2f}"
    draw.text((20, height - 40), total_text, font=font_bold, fill="black")

    # Final rounded card
    final = card

    buffer = BytesIO()
    final.save(buffer, format="PNG")
    return buffer.getvalue()
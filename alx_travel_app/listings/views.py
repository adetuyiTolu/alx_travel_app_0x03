import uuid
from django.shortcuts import render

from rest_framework import viewsets
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests 
import os
from celery import shared_task
from django.core.mail import send_mail

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

@api_view(['POST'])
def initiate_payment(request, booking_id):
    
    CHAPA_API_KEY = os.getenv("CHAPA_API_KEY")
    CHAPA_BASE_URL = "https://api.chapa.co/v1/transaction/initialize"
    booking = Booking.objects.get(id=booking_id)
    print(f"Email is {booking.user.email}")
    tx_ref= f"tx-{uuid.uuid4()}"
    data = {
        "amount": str(booking.total_price),
        "email": booking.user.email,
        "tx_ref":tx_ref ,
        "callback_url": "https://localhost/api/payments/verify/",
        "currency": "ETB"
    }
    headers = {"Authorization": f"Bearer {CHAPA_API_KEY}"}
    response = requests.post(CHAPA_BASE_URL, json=data, headers=headers)
    resp_data = response.json()

    if response.status_code == 200 and resp_data.get('status') == 'success':
        print(f"Response is {resp_data}")
        transaction_id = tx_ref
        Payment.objects.create(
            booking=booking,
            transaction_id=transaction_id,
            amount=booking.total_price,
            status='Pending'
        )
       
        return Response({
            "payment_url": resp_data['data']['checkout_url'],
            "transaction_id": transaction_id
        })
    return Response(resp_data, status=response.status_code)


@api_view(['POST'])
def verify_payment(request,transaction_id):
    
    CHAPA_VERIFY_URL = "https://api.chapa.co/v1/transaction/verify/"
    CHAPA_API_KEY = os.getenv("CHAPA_API_KEY")
   # transaction_id = request.data.get('transaction_id')
    headers = {"Authorization": f"Bearer {CHAPA_API_KEY}"}
    response = requests.get(f"{CHAPA_VERIFY_URL}{transaction_id}", headers=headers)
    resp_data = response.json()

    try:
        payment = Payment.objects.get(transaction_id=transaction_id)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

    if resp_data.get('status') == 'success':
        send_payment_confirmation_email.delay(payment.booking.user.email,payment.booking.id)
        payment.status = 'Completed'
        payment.save()
    else:
        payment.status = 'Failed'
        payment.save()
    
    return Response({"status": payment.status})


@shared_task
def send_payment_confirmation_email(user_email, booking_id):
    send_mail(
        subject="Payment Successful",
        message=f"Your payment for booking {booking_id} is successful!",
        from_email="no-reply@yourdomain.com",
        recipient_list=[user_email]
    )

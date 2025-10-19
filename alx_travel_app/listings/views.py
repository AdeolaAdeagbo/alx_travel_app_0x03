from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


@api_view(['POST'])
def initiate_payment(request):
    booking_id = request.data.get('booking_id')
    email = request.data.get('email')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    
    if not all([booking_id, email, first_name, last_name]):
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        booking = Booking.objects.get(id=booking_id)
        num_nights = (booking.end_date - booking.start_date).days
        total_amount = float(booking.listing.price_per_night) * num_nights
        tx_ref = f"booking-{booking_id}-{int(time.time())}"
        
        chapa_url = "https://api.chapa.co/v1/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "amount": str(total_amount),
            "currency": "ETB",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": "http://localhost:8000/api/payments/verify/",
            "return_url": "http://localhost:8000/api/payments/success/"
        }
        
        response = requests.post(chapa_url, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('status') == 'success':
            payment = Payment.objects.create(
                booking=booking,
                amount=total_amount,
                transaction_id=tx_ref,
                status='pending'
            )
            
            return Response({
                "message": "Payment initiated successfully",
                "checkout_url": response_data['data']['checkout_url'],
                "payment_id": payment.id
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Failed to initiate payment",
                "details": response_data
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def verify_payment(request):
    """
    Verifies payment status with Chapa.
    
    Query parameter: tx_ref (transaction reference)
    Example: /api/payments/verify/?tx_ref=booking-1-1234567890
    """
    tx_ref = request.GET.get('tx_ref')
    
    if not tx_ref:
        return Response(
            {"error": "Transaction reference is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get payment from database
        payment = Payment.objects.get(transaction_id=tx_ref)
        
        # Verify with Chapa
        chapa_url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
        headers = {
            "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}"
        }
        
        response = requests.get(chapa_url, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('status') == 'success':
            # Update payment status
            chapa_status = response_data['data']['status']
            
            if chapa_status == 'success':
                payment.status = 'completed'
            elif chapa_status == 'failed':
                payment.status = 'failed'
            
            payment.save()
            
            return Response({
                "message": "Payment verified",
                "payment_status": payment.status,
                "amount": str(payment.amount),
                "booking_id": payment.booking.id
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Verification failed",
                "details": response_data
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
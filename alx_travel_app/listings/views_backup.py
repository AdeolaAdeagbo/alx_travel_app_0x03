from rest_framework import viewsets
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer

# NEW IMPORTS for payment
import requests
import os
import time
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Load environment variables
load_dotenv()


# EXISTING CODE - Keep this!
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


# NEW CODE - Add this payment view
@api_view(['POST'])
def initiate_payment(request):
    """
    Initiates a payment with Chapa for a booking.
    
    Expected request data:
    {
        "booking_id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    # Get data from request
    booking_id = request.data.get('booking_id')
    email = request.data.get('email')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    
    # Validate required fields
    if not all([booking_id, email, first_name, last_name]):
        return Response(
            {"error": "Missing required fields"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get the booking
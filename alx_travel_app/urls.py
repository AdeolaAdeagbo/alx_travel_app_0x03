from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from alx_travel_app.listings.views import (
    ListingViewSet, 
    BookingViewSet, 
    ReviewViewSet,
    initiate_payment,
    verify_payment  # ADD THIS
)

router = routers.DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/payments/initiate/', initiate_payment, name='initiate-payment'),
    path('api/payments/verify/', verify_payment, name='verify-payment'),  # ADD THIS
]
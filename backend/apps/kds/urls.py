from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketCocinaViewSet

router = DefaultRouter()
router.register(r'tickets', TicketCocinaViewSet, basename='ticket-cocina')

urlpatterns = [ path('', include(router.urls)) ]

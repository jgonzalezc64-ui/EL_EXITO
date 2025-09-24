from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TiendaViewSet, MesaViewSet,
    EstadoOrdenViewSet, TipoServicioViewSet,
    OrdenViewSet
)

router = DefaultRouter()
router.register(r'tiendas', TiendaViewSet, basename='tienda')
router.register(r'mesas', MesaViewSet, basename='mesa')
router.register(r'estados-orden', EstadoOrdenViewSet, basename='estado-orden')
router.register(r'tipos-servicio', TipoServicioViewSet, basename='tipo-servicio')
router.register(r'ordenes', OrdenViewSet, basename='orden')

urlpatterns = [ path('', include(router.urls)) ]

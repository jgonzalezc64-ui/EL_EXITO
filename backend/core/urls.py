from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Reservamos el prefijo de API (las apps se irán conectando aquí)
    path('api/v1/', include([])),  # lo iremos poblando en el PASO 6–8
    path('api/v1/catalogos/', include('apps.catalogos.urls')),
    path('api/v1/pedidos/', include('apps.pedidos.urls')),
    path('api/v1/pagos/', include('apps.pagos.urls')),
    path('api/v1/kds/', include('apps.kds.urls')),
    path('api/v1/menus/', include('apps.menus.urls')),
    path('api/v1/seguridad/', include('apps.seguridad.urls')),
]

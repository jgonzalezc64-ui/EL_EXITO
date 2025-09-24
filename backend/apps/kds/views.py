from django.db import transaction
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TicketCocina
from .serializers import TicketCocinaSerializer

class TicketCocinaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /kds/tickets/?estado=PENDIENTE|EN_PREPARACION|LISTO|ENTREGADO
    GET /kds/tickets/{id_ticket}/
    GET /kds/tickets/por-orden/{id_orden}/   (extra)
    Acciones:
      POST /kds/tickets/{id_ticket}/en-preparacion
      POST /kds/tickets/{id_ticket}/listo
      POST /kds/tickets/{id_ticket}/entregado
    """
    queryset = TicketCocina.objects.all().order_by('fecha_generado', 'id_ticket')
    serializer_class = TicketCocinaSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering = ['fecha_generado', 'id_ticket']

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    @action(detail=False, methods=['get'], url_path='por-orden/(?P<id_orden>[^/.]+)')
    def por_orden(self, request, id_orden=None):
        try:
            tk = TicketCocina.objects.get(id_orden=id_orden)
        except TicketCocina.DoesNotExist:
            return Response({"detail":"No existe ticket para esa orden"}, status=404)
        return Response(self.get_serializer(tk).data)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='en-preparacion')
    def en_preparacion(self, request, pk=None):
        return self._cambiar_estado(pk, 'EN_PREPARACION')

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='listo')
    def listo(self, request, pk=None):
        return self._cambiar_estado(pk, 'LISTO')

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='entregado')
    def entregado(self, request, pk=None):
        return self._cambiar_estado(pk, 'ENTREGADO')

    def _cambiar_estado(self, id_ticket, nuevo_estado):
        try:
            tk = TicketCocina.objects.get(pk=id_ticket)
        except TicketCocina.DoesNotExist:
            return Response({"detail":"Ticket no encontrado"}, status=404)
        tk.estado = nuevo_estado
        tk.save()
        return Response(self.get_serializer(tk).data, status=200)

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from apps.seguridad.permissions import IsAdmin

from .models import Tienda, Mesa, EstadoOrden, TipoServicio, Orden, OrdenDetalle, OrdenDetalleModificador
from .serializers import (
    TiendaSerializer, MesaSerializer, EstadoOrdenSerializer, TipoServicioSerializer,
    OrdenSerializer, OrdenDetalleSerializer, OrdenDetalleModSerializer
)

def _require_role(request, allowed_groups: list[str]):
    if not request.user or not request.user.is_authenticated:
        raise NotAuthenticated()
    if not request.user.groups.filter(name__in=allowed_groups).exists():
        raise PermissionDenied("No tiene permisos para esta acción")


# ---- CRUD simples ----

class BaseCRUD(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = []
    ordering = []

class TiendaViewSet(BaseCRUD):
    permission_classes = [IsAdmin]
    queryset = Tienda.objects.all().order_by('nombre')
    serializer_class = TiendaSerializer
    search_fields = ['nombre', 'codigo']
    ordering = ['nombre']

class MesaViewSet(BaseCRUD):
    permission_classes = [IsAdmin]
    queryset = Mesa.objects.select_related('id_tienda').all().order_by('id_tienda__nombre','codigo')
    serializer_class = MesaSerializer
    search_fields = ['codigo', 'ubicacion', 'id_tienda__nombre']
    ordering = ['id_tienda__nombre','codigo']

# ---- Solo lectura ----

class EstadoOrdenViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdmin]
    queryset = EstadoOrden.objects.all().order_by('nombre')
    serializer_class = EstadoOrdenSerializer

class TipoServicioViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TipoServicio.objects.all().order_by('nombre')
    serializer_class = TipoServicioSerializer

# ---- Orden: acciones de negocio ----

class OrdenViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrdenSerializer

    def get_queryset(self):
        return (Orden.objects
                .select_related('id_estado','id_tipo_servicio','id_mesa')
                .all()
                .order_by('-fecha_hora', '-id_orden'))

    # Listar
    def list(self, request, *args, **kwargs):
        ser = self.get_serializer(self.get_queryset(), many=True)
        return Response(ser.data)

    # Detalle
    def retrieve(self, request, pk=None, *args, **kwargs):
        o = self.get_queryset().get(pk=pk)
        return Response(self.get_serializer(o).data)

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path='abrir')
    def abrir(self, request):
        _require_role(request, ['ADMIN', 'MESERO'])
        """
        body: { id_tipo_servicio, id_mesa (opcional según servicio), id_mesero (opcional), observaciones (opcional) }
        """
        
        id_tipo_servicio = request.data.get('id_tipo_servicio')
        id_mesa = request.data.get('id_mesa')
        id_mesero = request.data.get('id_mesero')
        observaciones = request.data.get('observaciones')

        if not id_tipo_servicio:
            return Response({"detail":"id_tipo_servicio es requerido"}, status=400)

        # Estado inicial: ABIERTA (asume que existe en catálogo)
        try:
            estado_abierta = EstadoOrden.objects.get(nombre='ABIERTA')
        except EstadoOrden.DoesNotExist:
            return Response({"detail":"Estado 'ABIERTA' no existe en EstadoOrden"}, status=400)

        o = Orden.objects.create(
            fecha_hora=timezone.now(),
            id_mesa_id=id_mesa,
            id_mesero=id_mesero,
            id_estado_id=estado_abierta.id_estado,
            id_tipo_servicio_id=id_tipo_servicio,
            observaciones=observaciones,
            subtotal=0, descuento=0, total=0  # subtotal se recalcula por trigger
        )
        return Response(self.get_serializer(o).data, status=201)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='agregar-detalle')
    def agregar_detalle(self, request, pk=None):
        _require_role(request, ['ADMIN', 'MESERO'])
        """
        body: { id_producto, cantidad, precio_unitario, nota, modificadores?: [{id_modificador, cantidad, precio_extra}] }
        """
        campos = ('id_producto','cantidad','precio_unitario')
        if any(request.data.get(c) in (None, '') for c in campos):
            return Response({"detail":"id_producto, cantidad y precio_unitario son requeridos"}, status=400)

        o = Orden.objects.get(pk=pk)
        d = OrdenDetalle.objects.create(
            id_orden=o,
            id_producto=request.data['id_producto'],
            cantidad=request.data['cantidad'],
            precio_unitario=request.data['precio_unitario'],
            nota=request.data.get('nota')
        )
        # modificadores opcionales
        for m in request.data.get('modificadores', []):
            OrdenDetalleModificador.objects.create(
                id_detalle=d,
                id_modificador=m['id_modificador'],
                cantidad=m.get('cantidad', 1),
                precio_extra=m.get('precio_extra', 0)
            )
        return Response(OrdenDetalleSerializer(d).data, status=201)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='editar-detalle')
    def editar_detalle(self, request, pk=None):
        _require_role(request, ['ADMIN', 'MESERO'])
        """
        body: { id_detalle, cantidad?, precio_unitario?, nota?, modificadores?: replace: true/false, items: [...] }
        """
        id_detalle = request.data.get('id_detalle')
        if not id_detalle:
            return Response({"detail":"id_detalle es requerido"}, status=400)
        d = OrdenDetalle.objects.get(pk=id_detalle, id_orden_id=pk)

        # actualizar campos básicos si vienen
        for campo in ['cantidad','precio_unitario','nota']:
            if campo in request.data:
                setattr(d, campo, request.data[campo])
        d.save()

        mods_payload = request.data.get('modificadores')
        if mods_payload:
            replace = mods_payload.get('replace', False)
            items = mods_payload.get('items', [])
            if replace:
                OrdenDetalleModificador.objects.filter(id_detalle=d).delete()
            for m in items:
                # upsert simple
                obj, _ = OrdenDetalleModificador.objects.update_or_create(
                    id_detalle=d, id_modificador=m['id_modificador'],
                    defaults={
                        'cantidad': m.get('cantidad',1),
                        'precio_extra': m.get('precio_extra',0)
                    }
                )
        return Response(OrdenDetalleSerializer(d).data, status=200)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='eliminar-detalle')
    def eliminar_detalle(self, request, pk=None):
        _require_role(request, ['ADMIN', 'MESERO'])
        """
        body: { id_detalle }
        """
        id_detalle = request.data.get('id_detalle')
        if not id_detalle:
            return Response({"detail":"id_detalle es requerido"}, status=400)
        deleted, _ = OrdenDetalle.objects.filter(id_orden_id=pk, id_detalle=id_detalle).delete()
        if not deleted:
            return Response({"detail":"Detalle no encontrado"}, status=404)
        return Response(status=204)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='aplicar-descuento')
    def aplicar_descuento(self, request, pk=None):
        _require_role(request, ['ADMIN', 'MESERO'])
        """
        body: { descuento }
        """
        desc = request.data.get('descuento')
        if desc is None:
            return Response({"detail":"descuento es requerido"}, status=400)
        o = Orden.objects.get(pk=pk)
        o.descuento = desc
        o.save()
        return Response(self.get_serializer(o).data, status=200)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        _require_role(request, ['ADMIN', 'MESERO'])
        """
        body: { id_estado }
        (La lógica de máquina de estados se puede reforzar aquí si lo deseas)
        """
        id_estado = request.data.get('id_estado')
        if not id_estado:
            return Response({"detail":"id_estado es requerido"}, status=400)
        o = Orden.objects.get(pk=pk)
        o.id_estado_id = id_estado
        o.save()
        return Response(self.get_serializer(o).data, status=200)

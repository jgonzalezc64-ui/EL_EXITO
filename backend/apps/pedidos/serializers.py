from rest_framework import serializers
from .models import Tienda, Mesa, EstadoOrden, TipoServicio, Orden, OrdenDetalle, OrdenDetalleModificador

class TiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tienda
        fields = ['id_tienda', 'nombre', 'codigo', 'activa']

class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['id_mesa', 'codigo', 'ubicacion', 'activa', 'id_tienda']

class EstadoOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoOrden
        fields = ['id_estado', 'nombre']

class TipoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoServicio
        fields = ['id_tipo_servicio', 'nombre']

class OrdenDetalleModSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenDetalleModificador
        fields = ['id_detalle', 'id_modificador', 'cantidad', 'precio_extra']

class OrdenDetalleSerializer(serializers.ModelSerializer):
    mods = OrdenDetalleModSerializer(source='mods', many=True, read_only=True)

    class Meta:
        model = OrdenDetalle
        fields = ['id_detalle', 'id_orden', 'id_producto', 'cantidad', 'precio_unitario', 'nota', 'mods']

class OrdenSerializer(serializers.ModelSerializer):
    detalles = OrdenDetalleSerializer(many=True, read_only=True)
    estado = EstadoOrdenSerializer(source='id_estado', read_only=True)
    tipo_servicio = TipoServicioSerializer(source='id_tipo_servicio', read_only=True)

    class Meta:
        model = Orden
        fields = [
            'id_orden', 'fecha_hora', 'id_mesa', 'id_mesero',
            'id_estado', 'estado', 'id_tipo_servicio', 'tipo_servicio',
            'observaciones', 'subtotal', 'descuento', 'total',
            'detalles'
        ]

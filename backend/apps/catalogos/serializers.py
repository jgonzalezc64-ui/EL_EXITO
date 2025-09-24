from rest_framework import serializers
from .models import (
    Categoria,
    Producto,
    ModificadorGrupo,
    Modificador,
    ProductoModificador,
)

# ---------- Categorías y Productos ----------

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id_categoria', 'nombre', 'descripcion', 'activo']


class ProductoSerializer(serializers.ModelSerializer):
    # Campo anidado solo-lectura con la info de la categoría
    categoria = CategoriaSerializer(source='id_categoria', read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id_producto',
            'id_categoria',   # FK (id)
            'categoria',      # objeto anidado (read-only)
            'nombre',
            'descripcion',
            'precio_base',
            'activo',
            'requiere_cocina',
        ]


# ---------- Modificadores ----------

class ModificadorSerializer(serializers.ModelSerializer):
    # Grupo anidado opcional (read-only)
    grupo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Modificador
        fields = [
            'id_modificador',
            'id_grupo',          # FK (id)
            'grupo',             # objeto anidado opcional
            'nombre',
            'precio_extra',
            'activo',
        ]

    def get_grupo(self, obj):
        g = obj.id_grupo
        if not g:
            return None
        return {
            'id_grupo': g.id_grupo,
            'nombre': g.nombre,
            'minimo': g.minimo,
            'maximo': g.maximo,
            'obligatorio': g.obligatorio,
        }


class ModificadorGrupoSerializer(serializers.ModelSerializer):
    modificadores = ModificadorSerializer(many=True, read_only=True)

    class Meta:
        model = ModificadorGrupo
        fields = [
            'id_grupo',
            'nombre',
            'descripcion',
            'minimo',
            'maximo',
            'obligatorio',
            'modificadores',
        ]


# ---------- Producto ↔ Modificador (tabla puente) ----------

class ProductoModificadorSerializer(serializers.ModelSerializer):
    # Representaciones anidadas (opcionales) para ver info de ambos lados
    producto = serializers.SerializerMethodField(read_only=True)
    modificador = ModificadorSerializer(source='id_modificador', read_only=True)

    class Meta:
        model = ProductoModificador
        fields = [
            'id_producto',      # FK (id)
            'id_modificador',   # FK (id)
            'producto',         # objeto anidado (compacto)
            'modificador',      # objeto anidado (detallado)
        ]

    def get_producto(self, obj):
        p = obj.id_producto
        if not p:
            return None
        return {
            'id_producto': p.id_producto,
            'id_categoria': p.id_categoria_id,
            'nombre': p.nombre,
            'precio_base': str(p.precio_base),
            'requiere_cocina': p.requiere_cocina,
            'activo': p.activo,
        }

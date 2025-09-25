Accesos por rol (qué puede ver / hacer)

ADMIN
    Seguridad
        Login/refresh, ver perfil (/seguridad/...)
        CRUD usuarios y grupos (/seguridad/users/, /seguridad/groups/)

    Catálogos (/catalogos/...)
        CRUD completo de Categoria, Producto, ModificadorGrupo, Modificador
        Gestiona relaciones ProductoModificador (crear/eliminar vínculos)

    Pedidos (/pedidos/...)
        CRUD de Tienda, Mesa
        Ver EstadoOrden, TipoServicio
        Acciones de orden: abrir, agregar/editar/eliminar detalle, aplicar descuento, cambiar estado

    Pagos (/pagos/...)
        Ver métodos
        Registrar pagos (y cerrar orden si suma ≥ total)

    KDS 
        Ver tickets
        Cambiar estados: en-preparacion, listo, entregado

    Menús (/menus/...)
        CRUD de Menu, MenuSeccion, MenuItem
        Acciones: publicar/despublicar, reordenar secciones/items, agregar items por categoría

MESERO

    Seguridad
        Login/refresh, ver perfil

    Catálogos
        Lectura de Categoria, Producto, ModificadorGrupo, Modificador

    Pedidos
        Ver EstadoOrden, TipoServicio
        Acciones de orden: abrir, agregar/editar/eliminar detalle, aplicar descuento, cambiar estado

    KDS 
        Lectura de tickets (listar, por-orden, detalle)
        No puede cambiar estados

    Pagos / Menús
        Sin permisos (403 en registrar pago y CRUD de menús)

CAJA

    Seguridad
        Login/refresh, ver perfil

    Catálogos
        Lectura de catálogos

    Pagos
        Ver métodos
        Registrar pagos (cierra orden si corresponde)

    Pedidos/KDS/Menús
        Sin acciones de negocio (puede recibir 403 si intenta)

COCINA

    Seguridad
        Login/refresh, ver perfil

    KDS
        Lectura de tickets
        Cambiar estados: en-preparacion, listo, entregado

    Catálogos/Pedidos/Pagos/Menús
        Lectura de catálogos (si abres lectura pública); no tiene acciones fuera de KDS

Lectura pública ()

GET /api/v1/catalogos/categorias/
GET /api/v1/catalogos/productos/
GET /api/v1/catalogos/modificador-grupos/
GET /api/v1/catalogos/modificadores/
Si más adelante se quiere exigir login también para lectura, elimina los AllowAny() en esas vistas.
from .database import get_connection
"""
Modelo Producto del sistema de inventario.

Este módulo define la clase Producto, la cual representa los productos
del sistema y gestiona sus operaciones CRUD.

Incluye lógica adicional como:
- Registro automático de movimientos de inventario
- Control de stock mínimo
- Borrado lógico de productos

Se integra con SQLite mediante consultas parametrizadas,
siguiendo el patrón MVC.
"""
class Producto:
    """
    Modelo que representa la entidad Producto.

    Gestiona información de inventario, incluyendo:
    - Datos básicos del producto
    - Control de stock
    - Relación con categoría
    - Registro de movimientos de inventario
    """
    def __init__(self, id_producto=None, nombre='', descripcion='', precio=0,
                 stock=0, stock_min=5, id_categoria=None, producto_activo=1, costo=0):
        self.id_producto = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock
        self.stock_min = stock_min
        self.id_categoria = id_categoria
        self.producto_activo = producto_activo
        self.costo = costo
        """
         Inicializa un objeto Producto.

        Args:
            id_producto (int, optional): ID del producto.
            nombre (str): Nombre del producto.
            descripcion (str): Descripción del producto.
            precio (float): Precio de venta.
            stock (int): Cantidad disponible.
            stock_min (int): Stock mínimo permitido.
            id_categoria (int | None): ID de la categoría.
            producto_activo (int): Estado lógico (1 activo, 0 inactivo).
            costo (float): Costo del producto.
        """
    @staticmethod
    def get_all(search=''):
        conn = get_connection()
        q = """
            SELECT p.*, c.nombre_categoria
            FROM productos p
            LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
            WHERE p.nombre LIKE ?
            ORDER BY p.id_producto
            """
        rows = conn.execute(q, (f'%{search}%',)).fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(id_producto):
        conn = get_connection()
        row = conn.execute("SELECT * FROM productos WHERE id_producto=?", (id_producto,)).fetchone()
        conn.close()
        return row

    @staticmethod
    def create(nombre, descripcion, precio, stock, stock_min, id_categoria, costo, activo=1):
        """
        Crea un nuevo producto en la base de datos.

        Además:
        - Registra un movimiento de inventario si el stock inicial es mayor a 0

        Args:
            nombre (str): Nombre del producto.
            descripcion (str): Descripción.
            precio (float): Precio de venta.
            stock (int): Cantidad inicial.
            stock_min (int): Stock mínimo.
            id_categoria (int | None): Categoría.
            costo (float): Costo del producto.
            activo (int): Estado lógico.

        Notas:
            - Se usa last_insert_rowid() para obtener el ID generado
            - Se registra automáticamente el movimiento de tipo 'Entrada'
            - Se mantiene consistencia (ACID) mediante commit()
        """
        conn = get_connection()
        conn.execute("""
            INSERT INTO productos (nombre, descripcion, precio, stock, stock_min, id_categoria, costo, producto_activo)
            VALUES (?,?,?,?,?,?,?,?)
        """, (nombre, descripcion, float(precio), int(stock), int(stock_min),
              id_categoria if id_categoria else None, float(costo), activo))
        
        # Movimiento de entrada inicial
        pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        if int(stock) > 0:
            conn.execute("""
                INSERT INTO movimiento_inventario (id_producto, cantidad_producto, valor_movimiento, tipo_movimiento, info_movimiento)
                VALUES (?,?,?,'Entrada','Stock inicial')
            """, (pid, int(stock), float(costo)*int(stock)))
        conn.commit()
        conn.close()

    @staticmethod
    def update(id_producto, nombre, descripcion, precio, stock, stock_min, id_categoria, costo, activo):
        conn = get_connection()
        old = conn.execute("SELECT stock FROM productos WHERE id_producto=?", (id_producto,)).fetchone()
        diff = int(stock) - old['stock']
        conn.execute("""
            UPDATE productos SET nombre=?, descripcion=?, precio=?, stock=?, stock_min=?,
            id_categoria=?, costo=?, producto_activo=? WHERE id_producto=?
        """, (nombre, descripcion, float(precio), int(stock), int(stock_min),
              id_categoria if id_categoria else None, float(costo), activo, id_producto))
        if diff != 0:
            tipo = 'Entrada' if diff > 0 else 'Salida'
            conn.execute("""
                INSERT INTO movimiento_inventario (id_producto, cantidad_producto, valor_movimiento, tipo_movimiento, info_movimiento)
                VALUES (?,?,?,'Ajuste','Ajuste manual desde edición')
            """, (id_producto, abs(diff), abs(diff)*float(costo)))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(id_producto):
        conn = get_connection()
        conn.execute("UPDATE productos SET producto_activo=0 WHERE id_producto=?", (id_producto,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_bajo_stock():
        conn = get_connection()
        rows = conn.execute("""
            SELECT p.*, c.nombre_categoria FROM productos p
            LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
            WHERE p.stock <= p.stock_min AND p.producto_activo=1
        """).fetchall()
        conn.close()
        return rows

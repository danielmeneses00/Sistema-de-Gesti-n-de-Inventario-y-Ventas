from .database import get_connection

class Producto:
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

from .database import get_connection

# ───── CATEGORIA ─────
class Categoria:
    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("""
            SELECT c.*, COUNT(p.id_producto) as total_productos
            FROM categoria c
            LEFT JOIN productos p ON c.id_categoria = p.id_categoria
            GROUP BY c.id_categoria
        """).fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        row = conn.execute("SELECT * FROM categoria WHERE id_categoria=?", (id,)).fetchone()
        conn.close()
        return row

    @staticmethod
    def create(nombre, descripcion):
        conn = get_connection()
        conn.execute("INSERT INTO categoria (nombre_categoria, descripcion_categoria) VALUES (?,?)",
                     (nombre, descripcion))
        conn.commit()
        conn.close()

    @staticmethod
    def update(id, nombre, descripcion):
        conn = get_connection()
        conn.execute("UPDATE categoria SET nombre_categoria=?, descripcion_categoria=? WHERE id_categoria=?",
                     (nombre, descripcion, id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(id):
        conn = get_connection()
        conn.execute("DELETE FROM categoria WHERE id_categoria=?", (id,))
        conn.commit()
        conn.close()


# ───── CLIENTE ─────
class Cliente:
    @staticmethod
    def get_all(search=''):
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM clientes WHERE nombre LIKE ? OR email LIKE ?
            ORDER BY id_cliente
        """, (f'%{search}%', f'%{search}%')).fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        row = conn.execute("SELECT * FROM clientes WHERE id_cliente=?", (id,)).fetchone()
        conn.close()
        return row

    @staticmethod
    def create(nombre, email, telefono, direccion):
        conn = get_connection()
        conn.execute("INSERT INTO clientes (nombre, email, telefono, direccion) VALUES (?,?,?,?)",
                     (nombre, email, telefono, direccion))
        conn.commit()
        conn.close()

    @staticmethod
    def update(id, nombre, email, telefono, direccion, activo):
        conn = get_connection()
        conn.execute("""UPDATE clientes SET nombre=?, email=?, telefono=?, direccion=?, cliente_activo=?
                        WHERE id_cliente=?""", (nombre, email, telefono, direccion, activo, id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(id):
        conn = get_connection()
        conn.execute("UPDATE clientes SET cliente_activo=0 WHERE id_cliente=?", (id,))
        conn.commit()
        conn.close()

    @staticmethod
    def historial(id_cliente):
        conn = get_connection()
        rows = conn.execute("""
            SELECT v.*, GROUP_CONCAT(p.nombre, ', ') as productos
            FROM ventas v
            LEFT JOIN detalle_venta dv ON v.id_venta = dv.id_venta
            LEFT JOIN productos p ON dv.id_producto = p.id_producto
            WHERE v.id_cliente=?
            GROUP BY v.id_venta
            ORDER BY v.fecha_venta DESC
        """, (id_cliente,)).fetchall()
        conn.close()
        return rows


# ───── VENTA ─────
class Venta:
    @staticmethod
    def get_all(search=''):
        conn = get_connection()
        rows = conn.execute("""
            SELECT v.*, c.nombre as nombre_cliente
            FROM ventas v
            LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
            WHERE v.numero_factura LIKE ? OR c.nombre LIKE ?
            ORDER BY v.fecha_venta DESC
        """, (f'%{search}%', f'%{search}%')).fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        venta = conn.execute("""
            SELECT v.*, c.nombre as nombre_cliente, c.email, c.telefono
            FROM ventas v LEFT JOIN clientes c ON v.id_cliente=c.id_cliente
            WHERE v.id_venta=?
        """, (id,)).fetchone()
        detalles = conn.execute("""
            SELECT dv.*, p.nombre FROM detalle_venta dv
            JOIN productos p ON dv.id_producto=p.id_producto
            WHERE dv.id_venta=?
        """, (id,)).fetchall()
        conn.close()
        return venta, detalles

    @staticmethod
    def create(id_cliente, items, metodo_pago, estado):
        """items = list of {id_producto, cantidad, precio_unidad}"""
        conn = get_connection()
        subtotal = sum(i['cantidad'] * i['precio_unidad'] for i in items)
        iva = subtotal * 0.19
        total = subtotal + iva

        # Numero factura
        count = conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
        numero = f"F-{str(count+1).zfill(4)}"

        conn.execute("""
            INSERT INTO ventas (numero_factura, id_cliente, subtotal_venta, precio_total, estado_venta, metodo_pago)
            VALUES (?,?,?,?,?,?)
        """, (numero, id_cliente if id_cliente else None, subtotal, total, estado, metodo_pago))
        vid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        for item in items:
            sub = item['cantidad'] * item['precio_unidad']
            conn.execute("""
                INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unidad, subtotal)
                VALUES (?,?,?,?,?)
            """, (vid, item['id_producto'], item['cantidad'], item['precio_unidad'], sub))
            # Descontar stock
            conn.execute("UPDATE productos SET stock = stock - ? WHERE id_producto=?",
                         (item['cantidad'], item['id_producto']))
            # Movimiento
            conn.execute("""
                INSERT INTO movimiento_inventario (id_producto, cantidad_producto, valor_movimiento, tipo_movimiento, info_movimiento)
                VALUES (?,?,?,'Salida',?)
            """, (item['id_producto'], item['cantidad'], sub, f'Venta #{numero}'))

        conn.commit()
        conn.close()
        return numero

    @staticmethod
    def stats_mes():
        conn = get_connection()
        r = conn.execute("""
            SELECT
                COUNT(*) as total_ventas,
                COALESCE(SUM(precio_total),0) as ingresos,
                COALESCE(AVG(precio_total),0) as ticket_promedio,
                SUM(CASE WHEN estado_venta='Pendiente' THEN 1 ELSE 0 END) as pendientes
            FROM ventas
            WHERE strftime('%Y-%m', fecha_venta) = strftime('%Y-%m', 'now')
        """).fetchone()
        conn.close()
        return r

    @staticmethod
    def ventas_7dias():
        conn = get_connection()
        rows = conn.execute("""
            SELECT DATE(fecha_venta) as dia, COALESCE(SUM(precio_total),0) as total
            FROM ventas
            WHERE fecha_venta >= DATE('now','-6 days')
            GROUP BY DATE(fecha_venta)
            ORDER BY dia
        """).fetchall()
        conn.close()
        return rows


# ───── MOVIMIENTO ─────
class Movimiento:
    @staticmethod
    def get_all(tipo=''):
        conn = get_connection()
        q = """
            SELECT m.*, p.nombre as nombre_producto
            FROM movimiento_inventario m
            JOIN productos p ON m.id_producto = p.id_producto
        """
        params = []
        if tipo:
            q += " WHERE m.tipo_movimiento=?"
            params.append(tipo)
        q += " ORDER BY m.fecha_movimiento DESC"
        rows = conn.execute(q, params).fetchall()
        conn.close()
        return rows

    @staticmethod
    def create(id_producto, cantidad, valor, tipo, info):
        conn = get_connection()
        conn.execute("""
            INSERT INTO movimiento_inventario (id_producto, cantidad_producto, valor_movimiento, tipo_movimiento, info_movimiento)
            VALUES (?,?,?,?,?)
        """, (id_producto, cantidad, valor, tipo, info))
        if tipo == 'Entrada':
            conn.execute("UPDATE productos SET stock = stock + ? WHERE id_producto=?", (cantidad, id_producto))
        elif tipo == 'Salida':
            conn.execute("UPDATE productos SET stock = stock - ? WHERE id_producto=?", (cantidad, id_producto))
        conn.commit()
        conn.close()

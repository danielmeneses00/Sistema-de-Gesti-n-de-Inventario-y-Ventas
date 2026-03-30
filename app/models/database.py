import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'inventario.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS categoria (
            id_categoria   INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_categoria   VARCHAR(50) NOT NULL,
            descripcion_categoria VARCHAR(255)
        );

        CREATE TABLE IF NOT EXISTS productos (
            id_producto    INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         VARCHAR(50) NOT NULL,
            descripcion    VARCHAR(255),
            precio         DECIMAL(10,2) NOT NULL DEFAULT 0,
            stock          INTEGER NOT NULL DEFAULT 0,
            stock_min      INTEGER NOT NULL DEFAULT 5,
            id_categoria   INTEGER,
            producto_activo BOOLEAN DEFAULT 1,
            costo          DECIMAL(10,2) DEFAULT 0,
            FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         VARCHAR(100) NOT NULL,
            email          VARCHAR(100),
            telefono       VARCHAR(20),
            direccion      VARCHAR(100),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cliente_activo BOOLEAN DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id_venta       INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_factura VARCHAR(50) UNIQUE,
            id_cliente     INTEGER,
            subtotal_venta DECIMAL(10,2) DEFAULT 0,
            precio_total   DECIMAL(10,2) DEFAULT 0,
            fecha_venta    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado_venta   VARCHAR(20) DEFAULT 'Pagada',
            metodo_pago    VARCHAR(20) DEFAULT 'Efectivo',
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        );

        CREATE TABLE IF NOT EXISTS detalle_venta (
            id_detalle     INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta       INTEGER NOT NULL,
            id_producto    INTEGER NOT NULL,
            cantidad       INTEGER NOT NULL,
            precio_unidad  DECIMAL(10,2) NOT NULL,
            subtotal       DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        );

        CREATE TABLE IF NOT EXISTS movimiento_inventario (
            id_movimiento  INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto    INTEGER NOT NULL,
            cantidad_producto INTEGER NOT NULL,
            valor_movimiento DECIMAL(10,2),
            tipo_movimiento VARCHAR(30) NOT NULL,
            info_movimiento VARCHAR(255),
            fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        );
    """)

    # Seed data
    cursor.execute("SELECT COUNT(*) FROM categoria")
    if cursor.fetchone()[0] == 0:
        cursor.executescript("""
            INSERT INTO categoria (nombre_categoria, descripcion_categoria) VALUES
                ('Electrodomésticos', 'Aparatos eléctricos para el hogar'),
                ('Periféricos', 'Teclados, mouse y accesorios de computador'),
                ('Monitores', 'Pantallas y displays'),
                ('Cables y Accesorios', 'Conectores y adaptadores'),
                ('Mobiliario', 'Sillas, escritorios y muebles');

            INSERT INTO productos (nombre, descripcion, precio, stock, stock_min, id_categoria, costo) VALUES
                ('Licuadora Oster 5V', 'Licuadora 5 velocidades 1.5L', 85000, 25, 5, 1, 55000),
                ('Teclado Mecánico RGB', 'Teclado mecánico retroiluminado', 120000, 2, 5, 2, 75000),
                ('Monitor 24 Full HD', 'Monitor IPS 1920x1080 75Hz', 580000, 15, 3, 3, 390000),
                ('Cable HDMI 2m', 'Cable HDMI 4K 2 metros', 18000, 3, 5, 4, 9000),
                ('Mouse Inalámbrico', 'Mouse óptico inalámbrico 2.4GHz', 45000, 1, 5, 2, 28000),
                ('Silla Ergonómica Pro', 'Silla de oficina con soporte lumbar', 650000, 8, 2, 5, 420000),
                ('Microondas 20L', 'Microondas digital 700W 20 litros', 220000, 12, 3, 1, 145000),
                ('Audífonos Bluetooth', 'Audífonos inalámbricos con cancelación de ruido', 195000, 20, 5, 2, 110000);

            INSERT INTO clientes (nombre, email, telefono, direccion) VALUES
                ('Carlos Ruiz',    'carlos.ruiz@email.com',   '3001234567', 'Calle 10 # 5-20, Cali'),
                ('Ana López',      'ana.lopez@gmail.com',     '3119876543', 'Av. 3N # 12-45, Cali'),
                ('Pedro García',   'pedrog@empresa.co',       '3155550001', 'Cra 1 # 8-30, Cali'),
                ('María Torres',   'mtorres@correo.com',      '3207771234', 'Calle 15 # 3-10, Cali'),
                ('Luis Martínez',  'lmartinez@trabajo.com',   '3184445678', 'Cra 5 # 20-15, Cali');
        """)

    conn.commit()
    conn.close()

from flask import Flask
from .models.database import init_db


def create_app():
    """
    Factory function que crea y configura la aplicación Flask.
    
    Realiza:
    - Creación de la instancia de Flask
    - Inicialización de la base de datos
    - Registro de blueprints (controladores)
    - Configuración general
    
    Returns:
        Flask: Instancia configurada de la aplicación
    """
    app = Flask(__name__)
    
    # Inicializar base de datos
    init_db()
    
    # Registrar blueprints (controladores)
    from .controllers import dashboard
    from .controllers import productos
    from .controllers import categorias
    from .controllers import clientes
    from .controllers import ventas
    from .controllers import inventario
    
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(productos.bp)
    app.register_blueprint(categorias.bp)
    app.register_blueprint(clientes.bp)
    app.register_blueprint(ventas.bp)
    app.register_blueprint(inventario.bp)
    
    return app

import os
from flask import Flask, redirect, url_for
from .models.database import init_db


def create_app():
    """
    Factory function que crea y configura la aplicación Flask.
    
    Realiza:
    - Creación de la instancia de Flask
    - Inicialización de la base de datos
    - Configuración de carpeta de templates
    - Registro de blueprints (controladores)
    - Configuración general
    
    Returns:
        Flask: Instancia configurada de la aplicación
    """
    # Configurar rutas personalizadas para templates y static
    app_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(app_dir, 'views')
    static_dir = os.path.join(app_dir, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
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
    
    # Ruta raíz que redirije al dashboard
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))
    
    return app

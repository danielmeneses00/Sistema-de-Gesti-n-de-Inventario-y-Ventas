from flask import Blueprint, render_template
from ..models.models import Categoria, Cliente
from ..models.producto import Producto

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
def index():
    """
    Dashboard principal que muestra estadísticas generales del sistema.
    """
    try:
        total_productos = len(Producto.get_all())
        total_categorias = len(Categoria.get_all())
        total_clientes = len(Cliente.get_all())
    except:
        total_productos = 0
        total_categorias = 0
        total_clientes = 0
    
    return render_template('dashboard.html',
                           total_productos=total_productos,
                           total_categorias=total_categorias,
                           total_clientes=total_clientes,
                           active='dashboard')

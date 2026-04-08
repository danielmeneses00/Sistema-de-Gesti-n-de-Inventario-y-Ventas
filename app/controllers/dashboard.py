from flask import Blueprint, render_template
from ..models.models import Categoria, Cliente, Venta, Movimiento
from ..models.producto import Producto
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
def index():
    """
    Dashboard principal que muestra estadísticas generales del sistema.
    """
    try:
        # Obtener productos con stock bajo
        bajo_stock = Producto.get_bajo_stock() if hasattr(Producto, 'get_bajo_stock') else []
        
        # Obtener totales
        total_productos = len(Producto.get_all())
        total_categorias = len(Categoria.get_all())
        total_clientes = len(Cliente.get_all())
        
        # Obtener todas las ventas para calcular estadísticas
        try:
            all_ventas = Venta.get_all()
            total_ventas = len(all_ventas) if all_ventas else 0
            ingresos = sum(v['precio_total'] for v in all_ventas if v['precio_total']) if all_ventas else 0
            ticket_promedio = ingresos / total_ventas if total_ventas > 0 else 0
        except:
            total_ventas = 0
            ingresos = 0
            ticket_promedio = 0
        
        # Estadísticas
        stats = {
            'ingresos': ingresos,
            'total_ventas': total_ventas,
            'ticket_promedio': ticket_promedio,
            'pendientes': 0
        }
        
        # Ventas de últimos 7 días
        ventas_7 = []
        try:
            if all_ventas:
                hoy = datetime.now()
                for i in range(7):
                    fecha = (hoy - timedelta(days=i)).date()
                    total_dia = sum(v['precio_total'] for v in all_ventas 
                                   if v.get('fecha_venta', '').startswith(str(fecha)))
                    ventas_7.append({'dia': str(fecha), 'total': total_dia})
                ventas_7.reverse()
        except:
            pass
        
        # Actividad reciente (movimientos)
        actividad = []
        try:
            if hasattr(Movimiento, 'get_all'):
                actividad = Movimiento.get_all()[:10]  # Últimos 10 movimientos
        except:
            pass
        
    except Exception as e:
        print(f"Error en dashboard: {e}")
        bajo_stock = []
        total_productos = 0
        total_categorias = 0
        total_clientes = 0
        stats = {'ingresos': 0, 'total_ventas': 0, 'ticket_promedio': 0, 'pendientes': 0}
        ventas_7 = []
        actividad = []
    
    return render_template('dashboard.html',
                           bajo_stock=bajo_stock,
                           total_productos=total_productos,
                           total_categorias=total_categorias,
                           total_clientes=total_clientes,
                           stats=stats,
                           ventas_7=ventas_7,
                           actividad=actividad,
                           active='dashboard')

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.models import Venta, Cliente
from ..models.producto import Producto

bp = Blueprint('ventas', __name__, url_prefix='/ventas')

@bp.route('/')
def index():
    search = request.args.get('q', '')
    ventas = Venta.get_all(search)
    stats = Venta.stats_mes()
    return render_template('ventas/index.html', ventas=ventas,
                           stats=stats, search=search, active='ventas')

@bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    clientes = Cliente.get_all()
    productos = Producto.get_all()

    if request.method == 'POST':
        try:
            items_json = request.form.get('items_json', '[]')
            items = json.loads(items_json)
            if not items:
                flash('Agrega al menos un producto.', 'error')
                return render_template('ventas/nueva.html', clientes=clientes,
                                       productos=productos, active='ventas')
            id_cliente = request.form.get('id_cliente') or None
            metodo = request.form.get('metodo_pago', 'Efectivo')
            estado = request.form.get('estado', 'Pagada')
            numero = Venta.create(id_cliente, items, metodo, estado)
            flash(f'Venta #{numero} registrada exitosamente.', 'success')
            return redirect(url_for('ventas.index'))
        except Exception as e:
            flash(f'Error al registrar venta: {e}', 'error')

    return render_template('ventas/nueva.html', clientes=clientes,
                           productos=productos, active='ventas')

@bp.route('/detalle/<int:id>')
def detalle(id):
    venta, detalles = Venta.get_by_id(id)
    if not venta:
        flash('Venta no encontrada.', 'error')
        return redirect(url_for('ventas.index'))
    return render_template('ventas/detalle.html', venta=venta,
                           detalles=detalles, active='ventas')

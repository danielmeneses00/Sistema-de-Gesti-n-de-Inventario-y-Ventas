from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.models import Movimiento
from ..models.producto import Producto

bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@bp.route('/')
def index():
    tipo = request.args.get('tipo', '')
    movimientos = Movimiento.get_all(tipo)
    productos = Producto.get_all()
    return render_template('inventario/index.html',
                           movimientos=movimientos,
                           productos=productos,
                           tipo_filtro=tipo,
                           active='inventario')

@bp.route('/registrar', methods=['POST'])
def registrar():
    try:
        id_producto = int(request.form.get('id_producto'))
        cantidad = int(request.form.get('cantidad', 0))
        tipo = request.form.get('tipo_movimiento', 'Entrada')
        info = request.form.get('info_movimiento', '')
        producto = Producto.get_by_id(id_producto)
        valor = cantidad * float(producto['costo'] or 0)

        if tipo == 'Salida' and producto['stock'] < cantidad:
            flash('No hay suficiente stock para registrar esta salida.', 'error')
        else:
            Movimiento.create(id_producto, cantidad, valor, tipo, info)
            flash('Movimiento registrado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('inventario.index'))

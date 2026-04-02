from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.producto import Producto
from ..models.models import Categoria

bp = Blueprint('productos', __name__, url_prefix='/productos')

@bp.route('/')
def index():
    search = request.args.get('q', '')
    productos = Producto.get_all(search)
    bajo_stock = Producto.get_bajo_stock()
    return render_template('productos/index.html',
        productos=productos, search=search,
        bajo_stock=bajo_stock, active='productos')

@bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    categorias = Categoria.get_all()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if not nombre:
            flash('El nombre es obligatorio.', 'error')
            return render_template('productos/form.html', categorias=categorias,
                                   producto=None, active='productos')
        try:
            Producto.create(
                nombre=nombre,
                descripcion=request.form.get('descripcion', ''),
                precio=request.form.get('precio', 0),
                stock=request.form.get('stock', 0),
                stock_min=request.form.get('stock_min', 5),
                id_categoria=request.form.get('id_categoria') or None,
                costo=request.form.get('costo', 0),
                activo=1
            )
            flash('Producto creado exitosamente.', 'success')
            return redirect(url_for('productos.index'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('productos/form.html', categorias=categorias,
                           producto=None, active='productos')

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    producto = Producto.get_by_id(id)
    categorias = Categoria.get_all()
    if not producto:
        flash('Producto no encontrado.', 'error')
        return redirect(url_for('productos.index'))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if not nombre:
            flash('El nombre es obligatorio.', 'error')
        else:
            try:
                Producto.update(
                    id_producto=id,
                    nombre=nombre,
                    descripcion=request.form.get('descripcion', ''),
                    precio=request.form.get('precio', 0),
                    stock=request.form.get('stock', 0),
                    stock_min=request.form.get('stock_min', 5),
                    id_categoria=request.form.get('id_categoria') or None,
                    costo=request.form.get('costo', 0),
                    activo=1 if request.form.get('activo') else 0
                )
                flash('Producto actualizado.', 'success')
                return redirect(url_for('productos.index'))
            except Exception as e:
                flash(f'Error: {e}', 'error')
    return render_template('productos/form.html', producto=producto,
                           categorias=categorias, active='productos')

@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    Producto.delete(id)
    flash('Producto desactivado.', 'success')
    return redirect(url_for('productos.index'))

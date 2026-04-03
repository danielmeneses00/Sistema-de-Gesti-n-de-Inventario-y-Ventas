from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.models import Cliente

bp = Blueprint('clientes', __name__, url_prefix='/clientes')
"""
Módulo: clientes

Descripción:
    Define las rutas para la gestión de clientes.
    Permite listar, buscar, crear, editar y desactivar registros de Cliente.

Prefijo de URL:
    /clientes
"""


@bp.route('/')
def index():
    """
    Función: index

    Descripción:
        Muestra la lista de clientes. Permite filtrar resultados mediante
        un parámetro de búsqueda.

    Método HTTP:
        GET

    Ruta:
        /clientes/

    Parámetros de consulta:
        - q (str, opcional): texto de búsqueda

    Comportamiento:
        - Obtiene el valor de búsqueda desde la URL.
        - Recupera los clientes que coincidan con el filtro.

    Retorna:
        Renderiza la plantilla 'clientes/index.html' con:
            - clientes: lista de objetos Cliente
            - search: valor de búsqueda actual
            - active: identificador de navegación ('clientes')
    """
    search = request.args.get('q', '')
    clientes = Cliente.get_all(search)
    return render_template('clientes/index.html', clientes=clientes,
                           search=search, active='clientes')


@bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    """
    Función: nuevo

    Descripción:
        Gestiona la creación de un nuevo cliente. Muestra el formulario
        y procesa los datos enviados.

    Métodos HTTP:
        GET, POST

    Ruta:
        /clientes/nuevo

    Parámetros de formulario (POST):
        - nombre (str, obligatorio)
        - email (str, opcional)
        - telefono (str, opcional)
        - direccion (str, opcional)

    Comportamiento:
        - En GET: muestra el formulario vacío.
        - En POST:
            * Valida que el nombre no esté vacío.
            * Crea un nuevo cliente si la validación es correcta.
            * Muestra mensajes de éxito o error.

    Retorna:
        - GET: renderiza 'clientes/form.html'
        - POST válido: redirige a 'clientes.index'
    """
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if not nombre:
            flash('El nombre es obligatorio.', 'error')
        else:
            Cliente.create(nombre,
                           request.form.get('email', ''),
                           request.form.get('telefono', ''),
                           request.form.get('direccion', ''))
            flash('Cliente registrado.', 'success')
            return redirect(url_for('clientes.index'))
    return render_template('clientes/form.html', cliente=None, active='clientes')


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """
    Función: editar

    Descripción:
        Permite editar la información de un cliente existente. También
        muestra el historial asociado al cliente.

    Métodos HTTP:
        GET, POST

    Ruta:
        /clientes/editar/<id>

    Parámetros:
        - id (int): identificador del cliente

    Parámetros de formulario (POST):
        - nombre (str)
        - email (str)
        - telefono (str)
        - direccion (str)
        - activo (bool, opcional)

    Comportamiento:
        - Verifica si el cliente existe.
        - En GET:
            * Obtiene el historial del cliente.
            * Muestra el formulario con los datos actuales.
        - En POST:
            * Actualiza la información del cliente.
            * Convierte el campo 'activo' a 1 o 0.
            * Muestra un mensaje de confirmación.

    Retorna:
        - Si no existe: redirige a 'clientes.index'
        - GET: renderiza 'clientes/form.html'
        - POST válido: redirige a 'clientes.index'
    """
    cliente = Cliente.get_by_id(id)
    if not cliente:
        flash('Cliente no encontrado.', 'error')
        return redirect(url_for('clientes.index'))
    if request.method == 'POST':
        Cliente.update(id,
                       request.form.get('nombre', ''),
                       request.form.get('email', ''),
                       request.form.get('telefono', ''),
                       request.form.get('direccion', ''),
                       1 if request.form.get('activo') else 0)
        flash('Cliente actualizado.', 'success')
        return redirect(url_for('clientes.index'))
    historial = Cliente.historial(id)
    return render_template('clientes/form.html', cliente=cliente,
                           historial=historial, active='clientes')


@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    """
    Función: eliminar

    Descripción:
        Desactiva un cliente en lugar de eliminarlo físicamente.

    Método HTTP:
        POST

    Ruta:
        /clientes/eliminar/<id>

    Parámetros:
        - id (int): identificador del cliente

    Comportamiento:
        - Marca el cliente como inactivo en el sistema.
        - Muestra un mensaje de confirmación.

    Retorna:
        Redirige a la ruta 'clientes.index'
    """
    Cliente.delete(id)
    flash('Cliente desactivado.', 'success')
    return redirect(url_for('clientes.index'))
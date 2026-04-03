from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.models import Categoria

bp = Blueprint('categorias', __name__, url_prefix='/categorias')
"""
Módulo: categorias

Descripción:
    Define las rutas relacionadas con la gestión de categorías.
    Permite listar, crear, editar y eliminar registros de Categoria.

Prefijo de URL:
    /categorias
"""


@bp.route('/')
def index():
    """
    Función: index

    Descripción:
        Obtiene todas las categorías registradas y renderiza la vista principal.

    Método HTTP:
        GET

    Ruta:
        /categorias/

    Retorna:
        Renderiza la plantilla 'categorias/index.html' con:
            - categorias: lista de objetos Categoria
            - active: identificador de navegación ('categorias')
    """
    cats = Categoria.get_all()
    return render_template('categorias/index.html', categorias=cats, active='categorias')


@bp.route('/nueva', methods=['POST'])
def nueva():
    """
    Función: nueva

    Descripción:
        Crea una nueva categoría a partir de los datos enviados por formulario.
        Si el nombre está vacío, no se crea el registro.

    Método HTTP:
        POST

    Ruta:
        /categorias/nueva

    Parámetros de formulario:
        - nombre (str, obligatorio)
        - descripcion (str, opcional)

    Comportamiento:
        - Valida que el nombre no esté vacío.
        - Inserta una nueva categoría si la validación es correcta.
        - Muestra un mensaje de éxito o error usando flash.

    Retorna:
        Redirige a la ruta 'categorias.index'
    """
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'error')
    else:
        Categoria.create(nombre, request.form.get('descripcion', ''))
        flash('Categoría creada.', 'success')
    return redirect(url_for('categorias.index'))


@bp.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    """
    Función: editar

    Descripción:
        Actualiza los datos de una categoría existente identificada por su ID.

    Método HTTP:
        POST

    Ruta:
        /categorias/editar/<id>

    Parámetros:
        - id (int): identificador de la categoría

    Parámetros de formulario:
        - nombre (str, opcional)
        - descripcion (str, opcional)

    Comportamiento:
        - Actualiza el registro con los valores proporcionados.
        - Muestra un mensaje de confirmación.

    Retorna:
        Redirige a la ruta 'categorias.index'
    """
    Categoria.update(id, request.form.get('nombre', ''), request.form.get('descripcion', ''))
    flash('Categoría actualizada.', 'success')
    return redirect(url_for('categorias.index'))


@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    """
    Función: eliminar

    Descripción:
        Elimina una categoría según su ID. Si existen registros asociados
        (por ejemplo, productos), la eliminación puede fallar.

    Método HTTP:
        POST

    Ruta:
        /categorias/eliminar/<id>

    Parámetros:
        - id (int): identificador de la categoría

    Comportamiento:
        - Intenta eliminar la categoría.
        - Muestra un mensaje de éxito si se elimina correctamente.
        - Muestra un mensaje de error si ocurre una excepción.

    Retorna:
        Redirige a la ruta 'categorias.index'

    Posibles errores:
        - No se puede eliminar la categoría si tiene elementos asociados.
    """
    try:
        Categoria.delete(id)
        flash('Categoría eliminada.', 'success')
    except Exception:
        flash('No se puede eliminar: tiene productos asociados.', 'error')
    return redirect(url_for('categorias.index'))
# base/controllers/usuarios.py

from flask import redirect, request, session, Blueprint, flash, render_template
from base.models.usuario_models import Usuario
from bcrypt import hashpw, gensalt

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@bp.route('/')
def dashboard():
    """Muestra el dashboard del usuario autenticado"""
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión primero.", 'login')
        return redirect('/')
    
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    if not usuario:
        session.clear()
        flash("Usuario no encontrado.", 'login')
        return redirect('/')
    
    return render_template('dashboard.html', usuario=usuario)

@bp.route('/perfil')
def perfil():
    """Muestra el perfil del usuario"""
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión primero.", 'login')
        return redirect('/')
    
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    if not usuario:
        session.clear()
        flash("Usuario no encontrado.", 'login')
        return redirect('/')
    
    return render_template('dashboard.html', usuario=usuario)

@bp.route('/procesar_registro', methods=['POST'])
def procesar_registro():
    if not Usuario.validar_registro(request.form):
        return redirect('/')
    
    password_hash = hashpw(request.form['password'].encode('utf-8'), gensalt())
    data = {
        **request.form,
        'password': password_hash.decode('utf-8')
    }
    usuario_id = Usuario.guardar_usuario(data)
    session['usuario_id'] = usuario_id
    flash("¡Registro exitoso!", 'exito')
    return redirect('/usuarios')

@bp.route('/procesar_login', methods=['POST'])
def procesar_login():
    usuario_valido = Usuario.validar_login(request.form)
    if not usuario_valido:
        return redirect('/')

    usuario_db = Usuario.obtener_por_email(request.form)
    session['usuario_id'] = usuario_db.id
    flash(f"¡Bienvenido de nuevo, {usuario_db.nombre}!", 'exito')
    return redirect('/usuarios')

@bp.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión exitosamente.", 'exito')
    return redirect('/')

@bp.route('/editar')
def editar():
    """Muestra el formulario para editar el usuario"""
    if 'usuario_id' not in session:
        flash("Primero debes iniciar sesión.", 'login')
        return redirect('/')
    
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    if not usuario:
        session.clear()
        flash("Usuario no encontrado.", 'login')
        return redirect('/')
    
    return render_template('editar_usuario.html', usuario=usuario)

@bp.route('/procesar_actualizacion', methods=['POST'])
def procesar_actualizacion():
    """Procesa la actualización de datos del usuario"""
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión primero.", 'login')
        return redirect('/')
    
    if not Usuario.validar_actualizacion(request.form, session['usuario_id']):
        return redirect('/usuarios/editar')
    
    data = {
        'id': session['usuario_id'],
        'nombre': request.form['nombre'],
        'apellido': request.form['apellido'],
        'email': request.form['email']
    }
    
    # Si se proporcionó una nueva contraseña, hashearla y agregarla a los datos
    if request.form.get('password') and request.form['password'].strip():
        password_hash = hashpw(request.form['password'].encode('utf-8'), gensalt())
        data['password'] = password_hash.decode('utf-8')
    
    Usuario.actualizar_usuario(data)
    flash("¡Perfil actualizado exitosamente!", 'exito')
    return redirect('/usuarios')

@bp.route('/eliminar', methods=['POST'])
def eliminar():
    """Elimina la cuenta del usuario"""
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión primero.", 'login')
        return redirect('/')
    
    # Guardar el ID del usuario antes de eliminar la sesión
    usuario_id = session['usuario_id']
    
    # Eliminar el usuario de la base de datos
    Usuario.eliminar_usuario(usuario_id)
    
    # Limpiar la sesión
    session.clear()
    
    # Mensaje de confirmación
    flash("Tu cuenta ha sido eliminada exitosamente.", 'exito')
    return redirect('/')
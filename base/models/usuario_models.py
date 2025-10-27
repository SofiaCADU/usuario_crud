# Modelo de usuario

# Encapsula toda la logica relacionada con los usuarios en la base de datos.

from base.config.mysqlconnection import connectToMySQL
import re
from flask import flash
from bcrypt import checkpw

# Clase regular para validar email
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9]+\.[a-zA-Z]+$')

class Usuario:
    """
    Clase que representa a un usuario y sus operaciones en la base de datos.
    """
    db = "usuario_crud"  # Nombre de la base de datos (debe coincidir con tu BD en MySQL)

    def __init__(self, data):
        """
        Constructor: inicializa los atributos del usuario.
        """
        self.id = data['id']                                            
        self.nombre = data['nombre'].capitalize()                       
        self.apellido = data['apellido'].capitalize()                  
        self.email = data['email']                                      
        self.password = data['password']                               
        self.creado_en = data['creado_en']                             
        self.actualizado_en = data['actualizado_en']                    

    @classmethod
    def guardar_usuario(cls, data):
        """
        Guarda un nuevo usuario en la base de datos.
        """
        # Normaliza nombre y apellido antes de guardar
        data['nombre'] = data['nombre'].capitalize()
        data['apellido'] = data['apellido'].capitalize()
        query = "INSERT INTO usuarios (nombre, apellido, email, password) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s);"
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return resultado  # Devuelve el ID del nuevo usuario

    @classmethod
    def obtener_por_email(cls, data):
        """
        Obtiene un usuario por su email.
        """
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        resultado = connectToMySQL(cls.db).query_db(query, data)
        if not resultado:
            return False
        return cls(resultado[0])
    
    @classmethod
    def obtener_por_id(cls, usuario_id):
        """
        Obtener un usuario por su ID.
        """
        query = "SELECT * FROM usuarios WHERE id = %(id)s;"
        data = {'id': usuario_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        if not resultado:
            return None
        return cls(resultado[0])
    
    @classmethod
    def actualizar_usuario(cls, data):
        """
        Actualiza los datos de un usuario existente.
        """
        # Normaliza nombre y apellido antes de actualizar
        data['nombre'] = data['nombre'].capitalize()
        data['apellido'] = data['apellido'].capitalize()
        
        # Si se incluye password en los datos, actualizar también la contraseña
        if 'password' in data:
            query = "UPDATE usuarios SET nombre = %(nombre)s, apellido = %(apellido)s, email = %(email)s, password = %(password)s WHERE id = %(id)s;"
        else:
            query = "UPDATE usuarios SET nombre = %(nombre)s, apellido = %(apellido)s, email = %(email)s WHERE id = %(id)s;"
        
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return resultado
    
    @classmethod
    def eliminar_usuario(cls, usuario_id):
        """
        Elimina un usuario de la base de datos.
        """
        query = "DELETE FROM usuarios WHERE id = %(id)s;"
        data = {'id': usuario_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return resultado
    
    @staticmethod
    def validar_actualizacion(usuario, usuario_id):
        """
        Valida los datos del formulario de actualización.
        Devuelve True si todo es válido, False si hay errores.
        """
        is_valid = True
        
        # Validar que el email no esté usado por otro usuario
        query = "SELECT * FROM usuarios WHERE email = %(email)s AND id != %(id)s;"
        data = {'email': usuario['email'], 'id': usuario_id}
        resultado = connectToMySQL(Usuario.db).query_db(query, data)
        if resultado:
            flash("El email ya está siendo usado por otro usuario.", "actualizacion")
            is_valid = False
        
        # Validar formato de email
        if not EMAIL_REGEX.match(usuario['email']):
            flash("Formato de email es inválido.", "actualizacion")
            is_valid = False
        
        # Validar longitud del nombre
        if len(usuario['nombre']) < 3:
            flash("El nombre debe tener al menos 3 caracteres.", "actualizacion")
            is_valid = False
        
        # Validar longitud del apellido
        if len(usuario['apellido']) < 3:
            flash("El apellido debe tener al menos 3 caracteres.", "actualizacion")
            is_valid = False
        
        # Validar contraseña si se proporcionó
        if usuario.get('password') and usuario['password'].strip():
            # Validar longitud de contraseña
            if len(usuario['password']) < 8:
                flash("La contraseña debe tener al menos 8 caracteres.", "actualizacion")
                is_valid = False
            
            # Validar que las contraseñas coincidan
            if usuario.get('confirm_password') and usuario['password'] != usuario['confirm_password']:
                flash("Las contraseñas no coinciden.", "actualizacion")
                is_valid = False
        
        return is_valid
    
    @staticmethod
    def validar_registro(usuario):
        """
        Valida los datos del formulario de registro.
        Devuelve True si todo es valido, False si hay errores (y los muestra con flash).
        """
        is_valid = True
        
        # Validar que el email no esté registrado
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        resultado = connectToMySQL(Usuario.db).query_db(query, usuario)
        if resultado:
            flash("El email ya está registrado.", "registro")
            is_valid = False
        
        # Validar formato de email
        if not EMAIL_REGEX.match(usuario['email']):
            flash("Formato de email es inválido.", "registro")
            is_valid = False
        
        # Validar longitud del nombre
        if len(usuario['nombre']) < 3:
            flash("El nombre debe tener al menos 3 caracteres.", "registro")
            is_valid = False
        
        # Validar longitud del apellido
        if len(usuario['apellido']) < 3:
            flash("El apellido debe tener al menos 3 caracteres.", "registro")
            is_valid = False
        
        # Validar longitud de contraseña
        if len(usuario['password']) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "registro")
            is_valid = False
        
        # Validar que las contraseñas coincidan
        if usuario['password'] != usuario['confirm_password']:
            flash("Las contraseñas no coinciden.", "registro")
            is_valid = False
        
        return is_valid
    
    @staticmethod
    def validar_login(usuario):
        """
        Valida los datos del formulario de inicio de login.
        Devuelve True si el usuario existe y la contraseña es correcta.
        """
        is_valid = True
        
        # Verificar que el usuario exista
        user_in_db = Usuario.obtener_por_email(usuario)
        if not user_in_db:
            flash("Email no registrado.", 'login')
            is_valid = False
        else:
            # Verificar que la contraseña sea correcta
            if not checkpw(usuario['password'].encode('utf-8'), user_in_db.password.encode('utf-8')):
                flash("Contraseña incorrecta.", 'login')
                is_valid = False
        
        return is_valid
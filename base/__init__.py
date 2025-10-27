from flask import Flask, render_template, session, redirect, flash
from datetime import datetime
from base.controllers.usuarios import bp as usuarios_bp
# from base.controllers.citas import bp as citas_bp

# importar controllers

# definir un filtro de jinja2 para formatear fechas
def format_date(value, format='%d/%m/%Y'):
    """Convierte una cadena de fechas en un objeto datetime y lo formatea."""
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d')
    return value.strftime(format)

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DEBUG=True,
    )

    # Registrar los blueprints
    app.register_blueprint(usuarios_bp)
    # app.register_blueprint(citas_bp)

    # Registrar el filtro de la fecha en la aplicación
    app.add_template_filter(format_date)

    @app.route('/')
    def index():
        # Si el usuario ya está autenticado, redirigir al dashboard
        if 'usuario_id' in session:
            return redirect('/usuarios')
        return render_template('auth.html')
    
    return app
# Server.py

from base import create_app

app = create_app()

# Punto de entrada principal de la aplicacion flask
# Crear la instancia de la app y la ejecuta

if __name__ == "__main__":
    # Ejecuta la aplicacion en modo debug para desarrollo
    app.run(port= 5007, debug=True)

    # En el port coloquen 5000 + el numero de lista.
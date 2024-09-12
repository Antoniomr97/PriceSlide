# Importamos el objeto de la aplicación Flask
from app import app

# Este bloque de código garantiza que la aplicación solo iniciara si se ejecuta directamente en este archivo y no importado
if __name__ == "__main__":
    # Crea el contexto para controlar donde se ejecuta todo
    with app.app_context():
        # Se inicia el servidor con debug activo que permite ir editando cosas mientras esta corriendo el servidor y se actualiza solo
        app.run(debug=True)
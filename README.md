# gnuGame
Juego desarrollado para representar las licencias del Software Libre. En este caso utilizando licencia GNU GPL (Licencia Pública General de GNU)

# Ejemplos
<img src="doc/index.png?raw=true" alt="index.png">
<img src="doc/juego1.png?raw=true" alt="juego1.png">
<img src="doc/gana.png?raw=true" alt="gana.png">

### Instalación
1. Clonar el repositorio
2. Comprobar que existe una install de Python 2.7 y Django 1.10
3. Instalar los componentes <tt>pip install -r requirements.txt</tt>
2. Crear la base de datos <tt>createdb gnuGame</tt>
3. Realizar las migraciones <tt>python manage.py makemigrations</tt> and <tt>python manage.py migrate</tt>
4. Iniciar el servidor <tt>python manage.py runserver</tt>

### Configuración
Si se desea acceder al panel de administración se debe crear un super usuario:
1. <tt>python manage.py createsuperuser</tt>

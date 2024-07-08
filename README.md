# Documentación técnica: Visión Ciudadana
## Arquitectura
### Stack
La aplicación está escrita en [Python (3.11)](https://docs.python.org/3.11/) y se sostiene en [Django (4.2)](https://docs.djangoproject.com/en/4.2/) y [Postgres](https://www.postgresql.org/), el proceso de desarrollo está contenizado ([Docker Compose](https://docs.docker.com/compose/)). 
### Lineamientos
- Se intenta seguir de [The Twelve Factors](https://12factor.net/). 
- Se busca mantener el código desacoplado entre la interfáz y la lógica de negocio.
- Se establecen estándares de estilo como [Flake8](https://flake8.pycqa.org/en/latest/), [Black](https://github.com/psf/black) e [Isort](https://timothycrosley.github.io/isort/) a través de [pre-commit](https://pre-commit.com/).
- Uso de pruebas unitarios con [coverage](https://coverage.readthedocs.io/en/7.5.4/) cercano al 100%.
### Dominios
Se utilizan las aplicaciones de django para separar los dominios de las interfaces (API REST), distinguíendose por el sufijo de `_api`. Existen hasta el momento tres dominios:
- Public Queries (`public_queries`): Maneja la lógica y regristro de consultas así como el sistema de respuestas.
- Admin (`admin`): Concentra los componentes de administración y gestión de cuentas con capacidad de crear consultas.
- Users (`users`): Contiene el modelo de usuarios y cierta lógica asociada a éste.
Las aplicaciones de django que representan dominios pueden tener los siguientes paquetes:
-  `domain_logic`: contienen las clases que manejan toda la lógica asociada al dominio.
-  `lib`: están las constantes, excepciones y dataclases usadas como fuente para interactuar con el dominio.
-  `providers`: contienen módulos con funciones a modo de capa intermedia a la consulta y manipulación de los modelos, tomando el nombre del modelo cada módulo.
Además suelen incluir el módulo `services.py` que contiene las funciones para consumir desde afuera del dominio (acá se suelen usar las clases de `lib`). El resto de módulos o paquetes son los propios del framework.
Las interfaces (API) que existen serían:
- `public_queries_api`: API REST para ser consumida por el usuario que responde una pregunta.
- `admin_api`: API REST para ser consumida por los usuarios administradores o gestores de consultas.
#### Public Queries
Los módulos lógicos del dominio son los siguientes:
- `auth.py`: contiene la clase `CanSubmitPublicQuery` que gestiona si una consulta puede o no ser respondida.
- `base.py`: contiene la clase `ServiceBase` que sirve de clase abstracta para algunas clases lógicas.
- `exports.py`: contiene la clase `PublicQueryExporter` que permite exportar datos de una consulta a pdf.
- `factories.py`: contiene la clase `PublicQueryFactory` que maneja la creación y edición de las consultas.
- `restrictions.py`: contiene la función `query_can_edit_questions`que verifica si la consulta puede ser modificada según cantidad de respuestas que tenga.
- `returners.py`: contiene la clase `PublicQueryReturner`que centraliza la entrega de datos sobre consultas.
- `submit.py`: contiene la clase `SubmitResponseEngine` que contiene la lógica asociada a la respuesta a una consulta.
El frontend se 	maneja a través de dos vistas, la primera (`/public_queries/submit/<str:uuid>`) funciona como punto de entrada para la inicialización de la clase `QuerySubmitEngine` de Javascript ubicada en `/static/js/submit/engine.js` que consume la API REST `public_queries_api`; mientras que la segunda (`/public_queries/submitted/<str:uuid>`) corresponde a la vista una vez respondida la consulta. 
#### Admin
Funciona principalmente como punto de entrada para el levantamiento de la clase Javascript `AdminEngine` ubicada en `static/js/admin/engine.js` que consume la API REST de `admin_api`. Además contiene las vistas asociadas a la autentificación que podrían ser mejor ubicadas en `users`.
### Modelos
![Untitled (1)](https://github.com/Cegir-Project/app-consultas-ciudadanas/assets/52863930/af6dffa6-df0f-4758-b425-5523f4cc5a92)
## Desarrollo
### Entorno local
Para levantar el entorno de desarrollo local se requiere tener instalado [Docker Engine](https://docs.docker.com/engine/) o [Docker Desktop](https://www.docker.com/products/docker-desktop/) con [Docker Compose](https://docs.docker.com/compose/). Con el comando `make build` se inicia la construcción de las imágenes, luego el comando `make up` sirve para levantar todos los contenedores como un conjunto. Ahora se puede acceder a la aplicación en `http://localhost:8000`.
### Contribuciones
Para contribuir al código primero es necesario tener instalado [pre-commit](https://pre-commit.com/) en el equipo. Se recomienda utilizar el comando `make run` para levantar los contenedores pero ingresando a la terminal, esto faculta a utilizar comandos útiles para el desarrollo como:
- `dev test`: Permite correr pytest sobre el repositorio, todos los tests deben correr exitosamente para aportar.
- `dev cov`: Permite correr coverage para indicar el porcentaje de código testeado.
- `dev up`: Levanta el servidor de desarrollo en `http://localhost:8000`.
- `dev shell`: Para acceder a la consola de Django.
- `dev migrate`: Corre las migraciones sobre la base de datos.
- `dev makemigrations`: Crea las migraciones faltantes.

Para poder compilar los estáticos (Sass y JS) es necesario desde una terminal del host correr el comando `make assets`, esto levantará un contenedor que lo procesará.
Finalmente se ruega no realizar commit directos a la rama `main`, sino que crear una rama (`git checkout -b [nombre de la rama]`) y crear un pull request. Esto permitirá que [Github](https://github.com/Cegir-Project/app-consultas-ciudadanas) corra los tests y haga las confirmaciones necesarias antes de ingresar nuevo código.

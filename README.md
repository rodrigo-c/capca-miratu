# app-consultas-ciudadanas

Construir las imágenes de docker:

```sh
make build
```

Levantar entorno de desarrollo (`localhost:8000`) con BrowserSync (`localhost:3000`) (sincronización de estáticos tipo js, css).

```sh
make up
```

Levantar contenedor de django simple (permite usar breakpoint en la ejecución):

```sh
make run
$ dev up  # levanta servidor de desarrollo localhost:8000
$ dev shell # ejecuta una shell de django
$ dev help  # otros comandos
```

Ingresar con una shell al contenedor corriendo:

```sh
make bash
$
```

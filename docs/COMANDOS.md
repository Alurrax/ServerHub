# ServerHub — Guía rápida de comandos

Referencia operativa para administrar, desarrollar, probar y diagnosticar ServerHub.

> **Directorio principal del proyecto**
>
> `/home/alurrax/proyectos/serverhub`

---

# 1. INICIO RÁPIDO

## Ir al proyecto

```bash
cd ~/proyectos/serverhub
```

`cd` significa **change directory**.

Nos posiciona en la raíz del proyecto ServerHub. La mayoría de los comandos
`docker compose` deben ejecutarse desde aquí porque aquí se encuentra
`compose.yml`.

---

## Ver estado general de ServerHub

```bash
docker compose ps
```

Muestra los servicios definidos en `compose.yml`.

Actualmente deberían aparecer:

- `serverhub-api`
- `serverhub-db`

Ejemplo:

```text
NAME            SERVICE   STATUS
serverhub-api   api       Up
serverhub-db    db        Up
```

Si aparece `Up`, el contenedor está ejecutándose.

---

## Levantar ServerHub

```bash
docker compose up -d
```

### Qué significa

- `docker compose`: administra los servicios definidos en `compose.yml`.
- `up`: crea/inicia los servicios.
- `-d`: detached mode; los deja funcionando en segundo plano.

Normalmente este es el comando que utilizaremos para iniciar ServerHub.

---

## Comprobar que API y PostgreSQL funcionan

```bash
curl http://127.0.0.1:8000/health
```

`curl` realiza una petición HTTP.

Actualmente esperamos:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

Esto comprueba dos cosas:

1. FastAPI está funcionando.
2. FastAPI puede conectarse a PostgreSQL.

---

## Ver estado de Git

```bash
git status
```

Indica:

- rama actual;
- archivos modificados;
- archivos nuevos;
- archivos preparados para commit;
- estado respecto de GitHub.

Conviene ejecutarlo frecuentemente.

---

# 2. DOCKER COMPOSE

Docker Compose administra el conjunto completo de servicios de ServerHub.

Actualmente:

```text
Docker Compose
│
├── api
│   └── FastAPI
│
└── db
    └── PostgreSQL
```

---

## Levantar servicios

```bash
docker compose up -d
```

Inicia todos los servicios.

No reconstruye necesariamente las imágenes si ya existen.

---

## Reconstruir y levantar

```bash
docker compose up -d --build
```

Utilizar cuando cambiemos:

- código que está copiado dentro de la imagen;
- `Dockerfile`;
- `requirements.txt`;
- dependencias;
- archivos necesarios durante el build.

`--build` obliga a Docker Compose a comprobar/reconstruir las imágenes.

En nuestro entorno actual es habitual después de modificar código Python,
porque el código se copia a la imagen mediante el Dockerfile.

---

## Detener servicios sin eliminarlos

```bash
docker compose stop
```

Los contenedores dejan de ejecutarse, pero siguen existiendo.

Posteriormente podemos ejecutar:

```bash
docker compose start
```

---

## Volver a iniciar servicios detenidos

```bash
docker compose start
```

Arranca los contenedores existentes.

No reconstruye imágenes.

---

## Reiniciar servicios

```bash
docker compose restart
```

Equivale conceptualmente a detener y volver a iniciar.

Útil cuando un servicio necesita reiniciarse pero no hemos cambiado la imagen.

---

## Bajar ServerHub

```bash
docker compose down
```

Hace:

1. detiene los contenedores;
2. elimina los contenedores;
3. elimina la red creada por Compose.

Pero **NO elimina los volúmenes persistentes por defecto**.

Por lo tanto PostgreSQL debería conservar sus datos.

---

## ⚠️ Borrar también los volúmenes

```bash
docker compose down -v
```

**CUIDADO.**

`-v` elimina los volúmenes asociados.

En ServerHub esto puede significar eliminar:

```text
postgres_data
```

y con ello los datos de PostgreSQL.

No utilizar salvo que queramos deliberadamente reinicializar la base de datos.

---

# 3. CONTROLAR SERVICIOS INDIVIDUALES

Nuestros nombres de servicio en Compose son:

```text
api
db
```

---

## Detener PostgreSQL

```bash
docker compose stop db
```

Detiene solamente la base de datos.

La API seguirá ejecutándose, pero las operaciones que requieran PostgreSQL
deberían fallar.

Esto es útil para probar tolerancia a fallos.

---

## Iniciar PostgreSQL

```bash
docker compose start db
```

---

## Reiniciar PostgreSQL

```bash
docker compose restart db
```

---

## Detener FastAPI

```bash
docker compose stop api
```

---

## Iniciar FastAPI

```bash
docker compose start api
```

---

## Reiniciar FastAPI

```bash
docker compose restart api
```

---

# 4. LOGS DE DOCKER

Los logs son una de las primeras herramientas que debemos utilizar cuando
algo falla.

---

## Ver logs de todos los servicios

```bash
docker compose logs
```

Muestra los mensajes generados por los contenedores.

---

## Seguir logs en tiempo real

```bash
docker compose logs -f
```

`-f` significa **follow**.

La terminal queda mostrando los nuevos mensajes a medida que aparecen.

Salir con:

```text
Ctrl + C
```

Esto no detiene los contenedores; solamente deja de mostrar los logs.

---

## Logs de FastAPI

```bash
docker compose logs -f api
```

Muy útil cuando:

- FastAPI no arranca;
- un endpoint genera error;
- hay problemas Python;
- falla SQLAlchemy;
- falla la conexión a PostgreSQL.

---

## Logs de PostgreSQL

```bash
docker compose logs -f db
```

Útil para:

- errores de inicio;
- problemas de autenticación;
- errores SQL;
- problemas con almacenamiento.

---

## Mostrar las últimas 100 líneas

```bash
docker compose logs --tail=100 api
```

Evita mostrar todo el historial.

---

# 5. DOCKER GENERAL

## Ver contenedores funcionando

```bash
docker ps
```

Muestra solamente contenedores activos.

---

## Ver todos los contenedores

```bash
docker ps -a
```

Incluye:

- ejecutándose;
- detenidos;
- finalizados.

---

## Ver imágenes Docker

```bash
docker images
```

Muestra imágenes disponibles localmente.

Por ejemplo:

```text
serverhub-api
postgres
hello-world
```

---

## Ver volúmenes

```bash
docker volume ls
```

Los volúmenes almacenan datos persistentes.

Nuestro PostgreSQL utiliza un volumen similar a:

```text
serverhub_postgres_data
```

El nombre exacto puede depender del nombre del proyecto Compose.

---

## Ver redes Docker

```bash
docker network ls
```

Docker Compose crea automáticamente una red para ServerHub.

Gracias a esa red:

```text
api
 │
 │ db:5432
 ▼
db
```

La API puede encontrar PostgreSQL utilizando el nombre del servicio `db`.

---

## Ver uso de espacio Docker

```bash
docker system df
```

Muestra espacio utilizado por:

- imágenes;
- contenedores;
- volúmenes;
- caché de construcción.

Importante porque el disco raíz de ServerHub tiene espacio limitado.

---

## Ver consumo de CPU y RAM

```bash
docker stats
```

Muestra en tiempo real:

- CPU;
- RAM;
- red;
- I/O;
- procesos.

Salir con:

```text
Ctrl + C
```

---

## Inspeccionar un contenedor

```bash
docker inspect serverhub-api
```

o:

```bash
docker inspect serverhub-db
```

Entrega información técnica detallada:

- IP interna;
- red;
- variables;
- volúmenes;
- configuración;
- estado.

---

# 6. ENTRAR A UN CONTENEDOR

## Abrir Bash dentro de FastAPI

```bash
docker compose exec api bash
```

Conceptualmente:

```text
Ubuntu LenoPC
    │
    └── Docker
          │
          └── serverhub-api
                  │
                  └── bash
```

Estamos ejecutando comandos **dentro del contenedor**.

---

## Salir

```bash
exit
```

Regresamos a la terminal normal de LenoPC.

---

## Ver archivos de la aplicación dentro del contenedor

```bash
docker compose exec api ls -la /app/app
```

Actualmente deberíamos encontrar archivos como:

```text
__init__.py
database.py
main.py
models.py
schemas.py
```

Es útil cuando sospechamos que Docker está utilizando una versión antigua del
código.

---

# 7. FASTAPI

## Probar endpoint raíz

```bash
curl http://127.0.0.1:8000/
```

Comprueba que la API responde.

---

## Health check

```bash
curl http://127.0.0.1:8000/health
```

Actualmente verifica FastAPI y la conexión con PostgreSQL.

---

## Consultar servicios

```bash
curl http://127.0.0.1:8000/services
```

Realiza:

```text
curl
 ↓
FastAPI
 ↓
SQLAlchemy
 ↓
PostgreSQL
 ↓
JSON
```

---

## Crear un servicio

```bash
curl -X POST http://127.0.0.1:8000/services \
  -H "Content-Type: application/json" \
  -d '{"name":"nginx","status":"running"}'
```

### Explicación

`-X POST`

Indica que utilizaremos el método HTTP POST.

`-H`

Agrega un header HTTP.

```text
Content-Type: application/json
```

indica que estamos enviando JSON.

`-d`

Contiene los datos enviados al servidor.

---

## Documentación automática FastAPI

FastAPI genera Swagger/OpenAPI automáticamente.

Dirección:

```text
http://127.0.0.1:8000/docs
```

Permite probar endpoints gráficamente.

---

# 8. POSTGRESQL

PostgreSQL se ejecuta dentro del servicio:

```text
db
```

---

## Entrar a PostgreSQL

```bash
docker compose exec db psql -U serverhub -d serverhub
```

### Explicación

`docker compose exec db`

Ejecuta algo dentro del contenedor PostgreSQL.

`psql`

Cliente de terminal de PostgreSQL.

`-U serverhub`

Usuario de PostgreSQL.

`-d serverhub`

Base de datos a utilizar.

---

## Listar tablas

Dentro de `psql`:

```text
\dt
```

Actualmente debería aparecer:

```text
services
```

---

## Ver estructura de una tabla

```text
\d services
```

Muestra:

- columnas;
- tipos;
- claves;
- restricciones;
- índices.

---

## Consultar registros

```sql
SELECT * FROM services;
```

---

## Consulta ordenada

```sql
SELECT id, name, status, created_at
FROM services
ORDER BY id;
```

---

## Salir de PostgreSQL

```text
\q
```

---

## Ejecutar SQL sin entrar a psql

```bash
docker compose exec db \
  psql -U serverhub -d serverhub \
  -c "SELECT * FROM services;"
```

`-c` permite ejecutar directamente una instrucción SQL.

---

## Ver base y usuario actual

```bash
docker compose exec db \
  psql -U serverhub -d serverhub \
  -c "SELECT current_database(), current_user;"
```

Esperamos:

```text
serverhub | serverhub
```

---

## Ver versión de PostgreSQL

```bash
docker compose exec db \
  psql -U serverhub -d serverhub \
  -c "SELECT version();"
```

---

# 9. PERSISTENCIA DE POSTGRESQL

La base utiliza un volumen Docker.

Conceptualmente:

```text
serverhub-db
     │
     ▼
PostgreSQL
     │
     ▼
postgres_data
```

El contenedor puede eliminarse y recrearse.

El volumen conserva los datos.

---

## Prueba de persistencia

Bajar contenedores:

```bash
docker compose down
```

Volver a crearlos:

```bash
docker compose up -d
```

Consultar:

```bash
curl http://127.0.0.1:8000/services
```

Si los registros continúan presentes, la persistencia funciona.

---

# 10. GIT — TRABAJO DIARIO

## Estado del repositorio

```bash
git status
```

Es uno de los comandos que más utilizaremos.

---

## Estado resumido

```bash
git status --short
```

Ejemplo:

```text
M  archivo.py
?? nuevo.py
```

`M` significa modificado.

`??` significa archivo nuevo todavía no rastreado.

---

## Ver modificaciones

```bash
git diff
```

Muestra cambios que todavía no hemos agregado al área de preparación.

---

## Agregar todos los cambios

```bash
git add .
```

Agrega todos los cambios desde el directorio actual.

Usarlo con atención.

Antes conviene ejecutar:

```bash
git status
```

---

## Agregar archivos específicos

Ejemplo:

```bash
git add apps/api/app/main.py
```

Es más seguro cuando queremos controlar exactamente qué entrará al commit.

---

## Ver lo que será guardado

```bash
git diff --cached
```

Muy importante.

Muestra exactamente el contenido preparado para el próximo commit.

Sirve para detectar:

- errores;
- archivos innecesarios;
- contraseñas;
- secretos;
- cambios accidentales.

---

## Crear commit

```bash
git commit -m "feat: descripción del cambio"
```

Ejemplo:

```bash
git commit -m "feat: integrate PostgreSQL with FastAPI"
```

---

## Enviar cambios a GitHub

```bash
git push
```

Envía los commits locales a:

```text
origin/main
```

---

## Descargar información de GitHub

```bash
git fetch
```

Actualiza la información de ramas remotas sin modificar directamente nuestros
archivos locales.

---

## Actualizar rama desde GitHub

```bash
git pull
```

Descarga e integra cambios remotos.

Conviene revisar antes:

```bash
git status
```

---

## Ver historial

```bash
git log --oneline -10
```

Muestra los últimos 10 commits.

---

## Ver ramas

```bash
git branch -vv
```

Muestra ramas locales y qué rama remota siguen.

---

## Ver repositorios remotos

```bash
git remote -v
```

Actualmente debe apuntar al repositorio ServerHub en GitHub.

---

# 11. CONVENCIÓN DE COMMITS

Usamos mensajes descriptivos.

```text
feat: nueva funcionalidad
fix: corrección de error
docs: documentación
chore: configuración o mantenimiento
refactor: reorganización de código
test: pruebas
```

Ejemplos:

```bash
git commit -m "feat: add services API"
```

```bash
git commit -m "fix: handle database connection error"
```

```bash
git commit -m "docs: add command reference"
```

---

# 12. SSH

## Desde Windows

Conectar utilizando nuestro alias:

```powershell
ssh serverhub
```

El alias está definido en:

```text
C:\Users\Alejandro\.ssh\config
```

---

## Conectar directamente por hostname

```powershell
ssh alurrax@LenoPC
```

---

## Conectar directamente por IP

```powershell
ssh alurrax@192.168.1.9
```

Útil para diagnóstico si el hostname no resuelve.

---

## Estado del servidor SSH

En Ubuntu:

```bash
systemctl status ssh --no-pager
```

---

## Ver si puerto 22 está escuchando

```bash
sudo ss -ltnp | grep ':22'
```

---

# 13. RED DEL SERVIDOR

## Ver IP rápidamente

```bash
ip -br addr
```

Nuestra interfaz Wi-Fi es:

```text
wlp0s20f3
```

---

## Ver rutas

```bash
ip route
```

Permite comprobar:

- gateway;
- interfaz utilizada;
- red local.

---

## Ver conexión NetworkManager

```bash
nmcli -f NAME,UUID,TYPE,DEVICE connection show --active
```

---

## Probar gateway

```bash
ping 192.168.1.1
```

Comprueba conectividad entre LenoPC y el router.

Salir:

```text
Ctrl + C
```

---

# 14. FIREWALL UFW

## Ver estado

```bash
sudo ufw status
```

---

## Ver reglas numeradas

```bash
sudo ufw status numbered
```

Actualmente ServerHub permite desde la LAN:

```text
22/tcp    SSH
Samba     Compartición de archivos
```

---

## Información detallada

```bash
sudo ufw status verbose
```

Muestra además:

- política predeterminada;
- logging;
- reglas IPv4/IPv6.

---

## ⚠️ Importante

No abrir puertos indiscriminadamente.

Antes de ejecutar algo como:

```bash
sudo ufw allow 8000/tcp
```

debemos decidir si realmente queremos que ese servicio sea accesible desde
toda la red.

---

# 15. SAMBA

Samba se mantiene porque LenoPC también se utiliza para otras tareas.

Carpeta compartida:

```text
/home/alurrax/Compartido
```

---

## Validar configuración

```bash
sudo testparm -s
```

Comprueba sintaxis y muestra configuración efectiva.

---

## Ver sesiones Samba

```bash
sudo smbstatus
```

Muestra usuarios y conexiones activas.

---

## Estado del servicio

```bash
systemctl status smbd --no-pager
```

---

# 16. RECURSOS DEL SERVIDOR

## Espacio de discos

```bash
df -h
```

`-h` significa human readable.

Muestra tamaños en GB/MB.

---

## Solo disco raíz

```bash
df -h /
```

Muy útil para ServerHub porque Docker utiliza almacenamiento del sistema.

---

## Memoria RAM

```bash
free -h
```

Muestra:

- RAM total;
- usada;
- libre;
- caché;
- swap.

---

## Procesos

```bash
top
```

Monitor básico de procesos.

Salir:

```text
q
```

---

## Recursos Docker

```bash
docker stats
```

Muestra recursos consumidos por cada contenedor.

---

# 17. PYTHON

## Ver versión

```bash
python3 --version
```

---

## Activar entorno virtual

Desde la raíz:

```bash
source .venv/bin/activate
```

Cuando está activo, normalmente el prompt muestra el entorno.

---

## Comprobar Python utilizado

```bash
which python
```

Esperamos:

```text
/home/alurrax/proyectos/serverhub/.venv/bin/python
```

---

## Ver pip

```bash
pip --version
```

---

## Instalar dependencias localmente

```bash
pip install -r apps/api/requirements.txt
```

Esto instala dependencias en `.venv`.

No confundir con las dependencias del contenedor Docker.

El Dockerfile también instala `requirements.txt`, pero **dentro de la imagen**.

---

# 18. ARCHIVOS IMPORTANTES DE SERVERHUB

```text
serverhub/
│
├── apps/
│   └── api/
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── database.py
│       │   ├── models.py
│       │   └── schemas.py
│       │
│       ├── Dockerfile
│       └── requirements.txt
│
├── docs/
│   ├── COMANDOS.md
│   └── sprints/
│
├── compose.yml
├── .env
├── .env.example
├── .gitignore
├── README.md
└── DIARIO.md
```

---

# 19. ARCHIVOS QUE NO DEBEN SUBIRSE A GIT

Especialmente:

```text
.env
.venv/
__pycache__/
```

Comprobar si `.env` está ignorado:

```bash
git check-ignore -v .env
```

Esto debería indicar qué regla de `.gitignore` está protegiéndolo.

---

# 20. DIAGNÓSTICO RÁPIDO

Cuando ServerHub no funcione, revisar en este orden.

## Paso 1 — ¿Docker funciona?

```bash
docker ps
```

---

## Paso 2 — ¿Los servicios están levantados?

```bash
docker compose ps
```

---

## Paso 3 — ¿FastAPI responde?

```bash
curl http://127.0.0.1:8000/health
```

---

## Paso 4 — ¿Qué dice FastAPI?

```bash
docker compose logs --tail=100 api
```

---

## Paso 5 — ¿Qué dice PostgreSQL?

```bash
docker compose logs --tail=100 db
```

---

## Paso 6 — ¿PostgreSQL responde?

```bash
docker compose exec db \
  psql -U serverhub -d serverhub \
  -c "SELECT 1;"
```

---

## Paso 7 — ¿Hay espacio?

```bash
df -h /
```

---

## Paso 8 — ¿Hay memoria?

```bash
free -h
```

---

## Paso 9 — ¿Qué cambió?

```bash
git status
```

y:

```bash
git diff
```

---

# 21. RUTINA DIARIA RECOMENDADA

## Al comenzar

```bash
cd ~/proyectos/serverhub

git status

docker compose ps

docker compose up -d

curl http://127.0.0.1:8000/health
```

Con esto comprobamos:

```text
Repositorio correcto     ✓
Git conocido             ✓
Contenedores activos     ✓
FastAPI activa           ✓
PostgreSQL conectado     ✓
```

---

## Mientras desarrollamos

Después de modificar código:

```bash
docker compose up -d --build
```

Probar:

```bash
curl http://127.0.0.1:8000/health
```

Revisar logs si falla:

```bash
docker compose logs -f api
```

---

## Antes de guardar en Git

```bash
git status
```

Después:

```bash
git diff
```

Agregar cambios:

```bash
git add .
```

Revisar exactamente lo preparado:

```bash
git diff --cached
```

Crear commit:

```bash
git commit -m "tipo: descripción"
```

Enviar:

```bash
git push
```

Comprobar:

```bash
git status
```

---

# 22. COMANDOS QUE REQUIEREN CUIDADO

## ⚠️ Eliminar volúmenes Docker

```bash
docker compose down -v
```

Puede eliminar los datos PostgreSQL.

---

## ⚠️ Limpiar Docker

Existen comandos como:

```bash
docker system prune
```

Pueden eliminar recursos Docker no utilizados.

No ejecutarlos mecánicamente.

Primero revisar:

```bash
docker system df
```

---

## ⚠️ Eliminar archivos Linux

```bash
rm
```

y especialmente:

```bash
rm -rf
```

pueden eliminar datos definitivamente.

Siempre revisar la ruta antes.

---

## ⚠️ Cambios de firewall

Antes de modificar UFW debemos asegurarnos de no bloquear SSH.

Comprobar primero:

```bash
sudo ufw status numbered
```

La regla SSH debe permanecer disponible desde nuestra LAN.

---

## ⚠️ Secretos y Git

Antes de cada commit importante:

```bash
git diff --cached
```

Nunca subir:

- contraseñas;
- claves privadas SSH;
- `.env`;
- tokens;
- credenciales.

---

# 23. CUATRO COMANDOS DE EMERGENCIA

Si no recordamos nada más:

```bash
cd ~/proyectos/serverhub
docker compose ps
curl http://127.0.0.1:8000/health
git status
```

Estos cuatro comandos permiten conocer rápidamente el estado general del
proyecto.

---

# 24. MAPA MENTAL

```text
WINDOWS
│
│ SSH / VS Code Remote
▼
LenoPC — Ubuntu
│
├── Git ───────────────────────────► GitHub
│
├── UFW
│    ├── SSH
│    └── Samba
│
└── Docker Compose
     │
     ├── api
     │    ├── Python
     │    ├── FastAPI
     │    ├── Pydantic
     │    ├── SQLAlchemy
     │    └── psycopg
     │          │
     │          │ db:5432
     │          ▼
     └── db
          └── PostgreSQL
                 │
                 ▼
          postgres_data
```

---

# 25. PRINCIPIO DE TRABAJO

```text
Modificar
   ↓
Construir
   ↓
Ejecutar
   ↓
Probar
   ↓
Revisar
   ↓
Documentar
   ↓
Commit
   ↓
Push
```

No avanzar acumulando cambios sin probar.

Cada commit importante debería representar un estado funcional de ServerHub.

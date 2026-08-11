# Bitácora de ServerHub

Registro cronológico del desarrollo, decisiones y principales hitos del proyecto ServerHub.

---

## 2026-08-08

### Inicio del proyecto

Se establece formalmente ServerHub como proyecto para construir una plataforma web de administración y monitoreo de servidores Linux.

El servidor principal utilizado para desarrollo es:

```text
LenoPC
```

Sistema operativo:

```text
Ubuntu 26.04 LTS
```

El desarrollo y administración también se realiza remotamente desde un PC Windows.

### Infraestructura completada

Se configuraron las herramientas principales del entorno:

- Ubuntu 26.04 LTS.
- Acceso SSH mediante clave.
- Alias SSH `serverhub`.
- VS Code Remote SSH.
- UFW.
- Samba en LAN.
- Git.
- Python 3.14.
- pip.
- entorno virtual Python.
- Docker Engine.
- Docker Compose.
- entorno VS Code local/remoto.

### Directorio principal

El proyecto se encuentra en:

```text
/home/alurrax/proyectos/serverhub
```

### Arquitectura inicial

ServerHub utiliza `LenoPC` como servidor y permite trabajar desde Windows mediante SSH o directamente desde Ubuntu.

La idea inicial se representa como:

```text
Cliente
   ↓
Servidor Linux
```

El objetivo es evolucionar hacia una plataforma web donde la administración no dependa exclusivamente de utilizar SSH y comandos manuales.

### Objetivo definido

Construir ServerHub incrementalmente como plataforma para:

- monitorear servidores;
- administrar servicios;
- administrar Docker;
- consultar almacenamiento;
- automatizar operaciones;
- registrar información;
- incorporar seguridad;
- aprender tecnologías modernas mediante un proyecto real.

### Próximo objetivo

Inicializar completamente el repositorio y desplegar los primeros servicios mediante Docker Compose.

---

## 2026-08-09

### Backend base

Se avanzó en la construcción del backend de ServerHub.

Tecnologías principales:

- Python.
- FastAPI.
- SQLAlchemy.
- PostgreSQL.
- Docker.
- Docker Compose.
- Uvicorn.
- Pydantic.

### Estructura de aplicaciones

Se comenzó a separar ServerHub en componentes:

```text
apps/
├── api/
└── agent/
```

Esta separación permite que la API principal no tenga que ejecutar directamente todas las operaciones privilegiadas del servidor.

### ServerHub API

Se implementó la API principal utilizando FastAPI.

Se incorporaron:

- endpoints de salud;
- estructura modular;
- routers;
- modelos SQLAlchemy;
- schemas Pydantic;
- conexión con PostgreSQL;
- configuración preparada para crecimiento.

La API se ejecuta mediante:

```text
Uvicorn
```

y queda disponible en:

```text
:8000
```

### PostgreSQL

Se incorporó PostgreSQL como base de datos del proyecto.

La base de datos se ejecuta mediante Docker.

Contenedor:

```text
serverhub-db
```

La API se ejecuta en:

```text
serverhub-api
```

La arquitectura comienza a tomar la forma:

```text
Cliente
   ↓
FastAPI
   ↓
PostgreSQL
```

### Docker Compose

Se utiliza Docker Compose para levantar los componentes principales.

Servicios principales:

```text
serverhub-api
serverhub-db
```

Esto permite definir infraestructura mediante código y reproducir el entorno de manera más controlada.

### Host Agent

Se tomó una decisión arquitectónica importante:

> Las operaciones directamente relacionadas con Ubuntu no deben ejecutarse indiscriminadamente desde la API dentro de Docker.

Se creó entonces el **ServerHub Host Agent**.

Arquitectura:

```text
Cliente
   ↓
ServerHub API
   ↓
Host Agent
   ↓
Ubuntu
```

El Host Agent se ejecuta directamente sobre Ubuntu.

Esto permite acceder de manera controlada a:

- systemd;
- Docker;
- información del host;
- almacenamiento;
- comandos específicos del sistema.

### Separación de responsabilidades

Se establece conceptualmente:

```text
Frontend
   ↓
API
   ↓
Agent
   ↓
Sistema operativo
```

La API funciona como intermediario entre el cliente y el servidor.

El cliente no debería comunicarse directamente con el Host Agent.

### Seguridad

Se comienza a aplicar una política basada en **whitelist**.

ServerHub no debe transformarse en una terminal remota que permita ejecutar cualquier comando.

Las operaciones administrativas deben estar explícitamente autorizadas.

Ejemplo:

```text
docker
  └── restart

smbd
  ├── start
  ├── stop
  └── restart
```

Un recurso no incluido en la lista puede consultarse, pero no necesariamente modificarse.

---

## 2026-08-10

### Información del sistema

Se implementaron endpoints para consultar información real del servidor `LenoPC`.

Datos disponibles:

- hostname;
- porcentaje de CPU;
- núcleos físicos;
- núcleos lógicos;
- load average de 1 minuto;
- load average de 5 minutos;
- load average de 15 minutos;
- memoria RAM;
- memoria disponible;
- swap;
- disco raíz;
- uptime.

Ejemplo conceptual:

```text
Host Agent
   ↓
psutil / sistema
   ↓
JSON
   ↓
ServerHub API
```

### Integración con Docker

Se agregó soporte para consultar Docker desde ServerHub.

El sistema puede obtener:

- contenedores;
- identificador;
- nombre;
- imagen;
- estado;
- puertos;
- fecha de creación.

Posteriormente se agregaron métricas:

- CPU;
- memoria;
- porcentaje de memoria;
- PIDs.

Contenedores principales:

```text
serverhub-api
serverhub-db
```

### Acciones Docker

Se agregó reinicio controlado de contenedores.

Los contenedores administrados actualmente son:

```text
serverhub-api
serverhub-db
```

Acción permitida:

```text
restart
```

La política se mantiene en el Host Agent.

### Servicios systemd

Se agregó integración con `systemctl`.

ServerHub puede consultar los servicios reales del servidor.

Se detectan aproximadamente:

```text
220 servicios
```

Información disponible:

- unit;
- nombre;
- estado de carga;
- estado activo;
- subestado;
- descripción.

Se implementaron operaciones:

```text
listar
consultar
iniciar
detener
reiniciar
```

Las acciones dependen de la whitelist.

### Servicios administrables

Actualmente:

```text
docker
```

Unidad:

```text
docker.service
```

Acciones:

```text
restart
```

También:

```text
smbd
```

Unidad:

```text
smbd.service
```

Acciones:

```text
start
stop
restart
```

Los demás servicios pueden visualizarse sin necesariamente poder modificarse.

### Discos

Se incorporó detección de almacenamiento mediante:

```text
lsblk
```

ServerHub puede obtener:

- discos físicos;
- particiones;
- filesystem;
- etiquetas;
- tamaño;
- espacio disponible;
- porcentaje utilizado;
- puntos de montaje.

Discos detectados:

```text
/dev/sda
/dev/nvme0n1
```

Tamaños aproximados:

```text
/dev/sda      931.51 GiB
/dev/nvme0n1  119.24 GiB
```

Partición Linux principal:

```text
/dev/sda3
```

Filesystem:

```text
ext4
```

Montaje:

```text
/
```

También se detectan particiones NTFS, EFI y swap.

### Testing

Se fortaleció la suite de pruebas.

Estado alcanzado:

```text
19 tests
```

Separación:

```text
15 tests normales
4 tests de integración
```

Se establecieron comandos:

```bash
make test
make test-integration
make check
```

### Tests normales

Los tests normales no deberían depender del estado real del servidor.

Para ello se incorporaron:

```text
mocks
```

Esto permite probar la API de manera reproducible.

### Tests de integración

Los tests de integración comprueban el flujo real:

```text
API
 ↓
Agent
 ↓
Host
```

Estos tests se mantienen separados porque dependen de infraestructura real.

### Mapa de dependencias

Se buscó una forma visual de comprender qué archivos dependen de cuáles.

Se probaron herramientas de análisis de dependencias Python.

Finalmente se creó una herramienta propia:

```text
scripts/serverhub_map.py
```

Comando:

```bash
make map
```

Genera:

```text
serverhub-global.dot
serverhub-global.svg
```

El objetivo del mapa es mostrar relaciones utilizando nombres reales de archivos.

Esto facilita entender visualmente la arquitectura.

### Archivos generados

Los gráficos generados no deben versionarse porque pueden reconstruirse.

Se agregaron al `.gitignore` archivos como:

```text
app.svg
serverhub-api-deps.svg
serverhub-api-internal.svg
serverhub-global.dot
serverhub-global.svg
```

### Git

El proyecto comienza a utilizar commits pequeños y relacionados con funcionalidades concretas.

Principio adoptado:

```text
desarrollar
   ↓
probar
   ↓
documentar
   ↓
commit
   ↓
push
```

---

## 2026-08-11

### Inicio del frontend

Se inició formalmente el frontend web de ServerHub.

Se utilizó:

```text
React
TypeScript
Vite
```

El proyecto se creó en:

```text
apps/web/
```

### Node.js

Node.js y npm se instalaron y administran mediante NVM.

Versiones utilizadas durante esta etapa:

```text
NVM   0.40.3
Node  v24.19.0
npm   11.17.0
```

### Vite

El frontend se ejecuta durante desarrollo mediante:

```bash
npm run dev -- --host 0.0.0.0
```

Servidor local:

```text
http://localhost:5173
```

Acceso desde la LAN:

```text
http://192.168.1.9:5173
```

Vite se ejecuta manualmente durante esta etapa.

Si la terminal donde se ejecuta Vite se cierra, el frontend deja de estar disponible.

### Primera conexión frontend/backend

El frontend comenzó a consumir información real de:

```text
http://192.168.1.9:8000
```

Se configuró CORS en FastAPI para permitir la comunicación entre:

```text
React :5173
   ↓
FastAPI :8000
```

### Dashboard

Se construyó el primer Dashboard funcional de ServerHub.

Muestra información real:

- hostname;
- CPU;
- RAM;
- disco raíz;
- uptime;
- swap.

Posteriormente se agregó Docker.

### Docker en Dashboard

Se incorporó una sección que muestra los contenedores.

Datos visibles:

- nombre;
- imagen;
- estado;
- CPU;
- memoria;
- PIDs.

Los datos se actualizan periódicamente.

### Polling

Se eligió inicialmente una estrategia simple:

```text
polling cada 5 segundos
```

Razones:

- fácil de entender;
- suficiente para esta etapa;
- no requiere WebSockets;
- mantiene baja complejidad.

### Reinicio Docker desde la web

Se implementó una acción real desde React.

Flujo:

```text
Usuario
   ↓
React
   ↓
FastAPI
   ↓
Host Agent
   ↓
Docker
```

Se comprobó el reinicio real de:

```text
serverhub-db
serverhub-api
```

Esto confirmó por primera vez que la interfaz web podía realizar una acción administrativa completa sobre el servidor.

### Refactor del frontend

A medida que `App.tsx` creció, se decidió separar responsabilidades.

Estructura:

```text
apps/web/src/
├── components/
│   └── Sidebar.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── System.tsx
│   ├── Services.tsx
│   └── Disks.tsx
├── services/
│   └── api.ts
├── types/
│   └── serverhub.ts
├── App.tsx
├── App.css
├── index.css
└── main.tsx
```

### Responsabilidades frontend

`main.tsx`

```text
punto de entrada React
```

`App.tsx`

```text
layout
navegación
selección de página
```

`components/`

```text
componentes reutilizables
```

`pages/`

```text
pantallas funcionales
```

`services/api.ts`

```text
comunicación HTTP
```

`types/serverhub.ts`

```text
contratos TypeScript
```

### Página Sistema

Se terminó la página:

```text
Sistema
```

Muestra:

- hostname;
- uptime;
- CPU;
- núcleos físicos;
- núcleos lógicos;
- load 1 minuto;
- load 5 minutos;
- load 15 minutos;
- RAM;
- swap;
- filesystem raíz.

La información se actualiza periódicamente.

### Página Servicios

Se creó una interfaz para visualizar los servicios systemd.

Funciones:

- listado;
- búsqueda;
- filtro Todos;
- filtro Activos;
- filtro Inactivos;
- filtro Administrables;
- descripción;
- estado;
- subestado.

Los servicios administrables muestran acciones.

Los demás muestran:

```text
Solo lectura
```

### Seguridad en Servicios

La interfaz respeta conceptualmente la política definida por el Host Agent.

Actualmente los servicios administrables son:

```text
docker
smbd
```

El backend sigue siendo la autoridad final para decidir si una acción está permitida.

Se identifica como mejora futura evitar duplicar esta información en React y hacer que la API entregue:

```text
managed
actions
```

### Página Discos

Se terminó la página:

```text
Discos
```

Muestra los discos físicos y sus particiones.

Información:

- nombre;
- dispositivo;
- tamaño;
- filesystem;
- etiqueta;
- uso;
- espacio disponible;
- punto de montaje.

Se muestran correctamente:

```text
sda
nvme0n1
```

### Estado visual del frontend

Al cierre de esta etapa existen cuatro vistas principales funcionales:

```text
Dashboard
Sistema
Servicios
Discos
```

Docker está integrado principalmente dentro del Dashboard.

### Validación frontend

Se establecieron dos comprobaciones antes de versionar cambios:

```bash
npm run build
npm run lint
```

Build:

```text
TypeScript
   ↓
Vite
```

Lint:

```text
Oxlint
```

Las comprobaciones terminaron correctamente:

```text
0 warnings
0 errors
```

### Git

Se versionaron los distintos bloques funcionales.

Entre los commits recientes se encuentran:

```text
feat: add system services management page
feat: add system and disks pages
docs: improve ServerHub README
docs: add ServerHub interface screenshots
```

La rama utilizada es:

```text
main
```

y se mantiene sincronizada con:

```text
origin/main
```

### README de GitHub

Se reemplazó el README inicial por una presentación más completa de ServerHub.

El nuevo README contiene:

- descripción;
- objetivo;
- arquitectura;
- funcionalidades;
- stack tecnológico;
- estructura del repositorio;
- flujo de peticiones;
- seguridad;
- instrucciones de desarrollo;
- testing;
- roadmap;
- filosofía del proyecto.

### Capturas

Se agregaron cuatro capturas reales de ServerHub:

```text
docs/images/
├── serverhub-dashboard.png
├── serverhub-sistema.png
├── serverhub-servicios.png
└── serverhub-discos.png
```

Las imágenes están versionadas en Git.

Commit:

```text
docs: add ServerHub interface screenshots
```

### Presentación del repositorio

Se decidió mejorar también la información visible en GitHub mediante:

- descripción del repositorio;
- Topics;
- README;
- capturas.

Topics propuestos:

```text
server-management
linux
ubuntu
react
typescript
fastapi
python
docker
postgresql
systemd
devops
```

### Documentación Obsidian

La documentación técnica se actualizó para reflejar el avance real.

Documentos actualizados:

```text
02 - Estado actual.md
08 - Desarrollo.md
10 - Frontend.md
11 - Roadmap.md
12 - Decisiones técnicas.md
```

Se agregó:

```text
13 - Git y Versionado.md
```

### Git y documentación

Se estableció como práctica:

> Primero versionar una funcionalidad estable y después actualizar la documentación para que represente el código realmente almacenado en Git.

### Arquitectura actual

Al cierre de esta etapa, ServerHub puede representarse como:

```text
Windows / Navegador
        |
        v
React + TypeScript + Vite
        |
        | HTTP
        v
ServerHub API
FastAPI :8000
        |
        +----------------------+
        |                      |
        v                      v
PostgreSQL              Host Agent :9000
serverhub-db                   |
                               +--> systemd
                               +--> Docker
                               +--> lsblk
                               |
                               v
                           Ubuntu Host
                            LenoPC
```

### Flujo completo de ejemplo

Consulta:

```text
Usuario abre Dashboard
        ↓
Dashboard.tsx
        ↓
services/api.ts
        ↓
FastAPI
        ↓
Host Agent
        ↓
Ubuntu / Docker
        ↓
JSON
        ↓
FastAPI
        ↓
React
        ↓
Dashboard actualizado
```

### Estado funcional

```text
Infraestructura          ✅
SSH                      ✅
Git                      ✅
Docker                   ✅
Docker Compose           ✅
FastAPI                  ✅
PostgreSQL               ✅
Host Agent               ✅
Información sistema      ✅
systemd                  ✅
Discos                   ✅
Docker stats             ✅
Docker restart           ✅
Testing                  ✅
Tests integración        ✅
Mocks                    ✅
Mapa dependencias        ✅
React                    ✅
TypeScript               ✅
Vite                     ✅
Dashboard                ✅
Sistema                  ✅
Servicios                ✅
Discos                   ✅
Build frontend           ✅
Lint frontend            ✅
README GitHub            ✅
Capturas GitHub          ✅
Obsidian                 ✅
```

### Funcionalidades pendientes

Todavía no implementadas:

```text
Autenticación
Usuarios
Roles y permisos
Nginx
Redis
CI/CD
GitHub Actions
Backups
Logs desde frontend
Métricas históricas
Prometheus
Grafana
Alertas
Automatización
IA
Multi-host
```

Redis se incorporará únicamente cuando exista una necesidad concreta.

### Estado de los Sprints

```text
Sprint 0 — Infraestructura
████████████████████ 100%

Sprint 1 — Plataforma base
████████████████░░░░ ~80%

Sprint 2 — Aplicación y experiencia
██████████████░░░░░░ ~70%

Sprint 3 — DevOps
█████░░░░░░░░░░░░░░░ ~25%

Sprint 4 — Operación
███░░░░░░░░░░░░░░░░░ ~15%

Sprint 5 — Automatización e IA
░░░░░░░░░░░░░░░░░░░░ 0%
```

Parte del trabajo de Sprint 3 y Sprint 4 fue adelantado durante la construcción de la plataforma.

### Punto de pausa

Se decidió detener temporalmente la incorporación de nuevas funcionalidades.

El motivo es consolidar el aprendizaje antes de aumentar la complejidad.

### Próximo objetivo

Realizar una revisión completa de ServerHub desde la base.

La revisión incluirá:

1. estructura del repositorio;
2. función de cada carpeta;
3. función de cada archivo;
4. imports y dependencias;
5. React;
6. componentes;
7. TypeScript;
8. Vite;
9. HTTP;
10. JSON;
11. FastAPI;
12. routers;
13. CORS;
14. Host Agent;
15. systemd;
16. Docker;
17. Docker Compose;
18. PostgreSQL;
19. SQLAlchemy;
20. Pydantic;
21. pytest;
22. mocks;
23. tests de integración;
24. Git;
25. Obsidian;
26. flujo completo de una petición.

El objetivo de esta revisión es entender **cómo funciona ServerHub completo y por qué se utilizó cada tecnología** antes de continuar con nuevas capas.

### Etapas posteriores

Después de consolidar la arquitectura actual se evaluará continuar con:

```text
Autenticación
      ↓
Usuarios y roles
      ↓
Nginx
      ↓
CI/CD
      ↓
Backups
      ↓
Observabilidad
```

---

## Principio de desarrollo

ServerHub se mantiene bajo un ciclo incremental:

```text
Planificar
    ↓
Diseñar
    ↓
Construir
    ↓
Probar
    ↓
Documentar
    ↓
Versionar
    ↓
Continuar
```

La prioridad no es solamente terminar una aplicación.

El proyecto también funciona como laboratorio práctico para comprender cómo se relacionan:

```text
Linux
Python
FastAPI
HTTP
React
TypeScript
Docker
PostgreSQL
systemd
Git
Testing
DevOps
```

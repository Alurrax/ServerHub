# ServerHub

Plataforma web para **monitorear y administrar un servidor Linux** desde una interfaz centralizada.

ServerHub combina un frontend web en React con una API FastAPI y un Host Agent que ejecuta operaciones controladas directamente sobre Ubuntu.

> Proyecto en desarrollo, orientado al aprendizaje práctico de arquitectura web, Linux, Docker, APIs, DevOps y administración de servidores.

---

## Vista general

ServerHub permite consultar y administrar información real del servidor:

- CPU
- RAM
- Swap
- Uptime
- Disco raíz
- Discos físicos y particiones
- Servicios `systemd`
- Contenedores Docker
- Métricas de contenedores
- Reinicio controlado de servicios y contenedores

---

## Arquitectura

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
```

La separación entre API y Host Agent es intencional:

- la **API** contiene la lógica de aplicación;
- el **Host Agent** ejecuta operaciones controladas sobre Ubuntu;
- PostgreSQL mantiene la persistencia;
- Docker Compose administra API y base de datos;
- React entrega la interfaz de usuario.

---

## Estado actual

### Dashboard

- CPU
- RAM
- disco raíz
- uptime
- swap
- estado Docker
- CPU/RAM/PIDs por contenedor
- actualización automática cada 5 segundos
- reinicio controlado de contenedores

### Sistema

- hostname
- núcleos físicos y lógicos
- CPU
- load average de 1, 5 y 15 minutos
- RAM
- swap
- filesystem raíz
- uptime

### Servicios

- listado real de servicios `systemd`
- búsqueda
- filtros por estado
- servicios administrables
- servicios de solo lectura
- reinicio controlado según política del Host Agent

Actualmente:

```text
docker
  restart

smbd
  start
  stop
  restart
```

### Discos

- discos físicos
- particiones
- filesystem
- etiquetas
- tamaño
- espacio disponible
- porcentaje de uso
- puntos de montaje

---

## Stack tecnológico

### Frontend

- React
- TypeScript
- Vite
- Oxlint
- CSS

### Backend

- Python
- FastAPI
- HTTPX
- SQLAlchemy
- Pydantic
- psutil

### Infraestructura

- Ubuntu
- Docker
- Docker Compose
- PostgreSQL 18
- systemd
- Uvicorn
- Git

### Testing

- pytest
- FastAPI TestClient
- tests de integración
- mocks

### Documentación

- Markdown
- Obsidian
- Graphviz
- mapa automático de dependencias

---

## Estructura del proyecto

```text
serverhub/
├── apps/
│   ├── agent/
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   ├── api/
│   │   ├── app/
│   │   │   ├── routers/
│   │   │   │   ├── services.py
│   │   │   │   └── system.py
│   │   │   ├── database.py
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── migrations/
│   │   └── tests/
│   │
│   └── web/
│       └── src/
│           ├── components/
│           │   └── Sidebar.tsx
│           ├── pages/
│           │   ├── Dashboard.tsx
│           │   ├── System.tsx
│           │   ├── Services.tsx
│           │   └── Disks.tsx
│           ├── services/
│           │   └── api.ts
│           ├── types/
│           │   └── serverhub.ts
│           └── App.tsx
│
├── docs/
├── infra/
├── scripts/
│   └── serverhub_map.py
├── compose.yml
├── Makefile
└── README.md
```

---

## Flujo de una petición

Ejemplo: obtener estadísticas Docker.

```text
React
  |
  | GET /system/docker/containers/serverhub-api/stats
  v
FastAPI
  |
  | HTTP
  v
Host Agent
  |
  | Docker CLI
  v
Docker Engine
  |
  v
Respuesta JSON
  |
  v
React Dashboard
```

---

## Seguridad

ServerHub aplica una política de **mínimo privilegio**.

El Host Agent no funciona como una terminal remota genérica.

Las operaciones administrativas pasan por listas explícitas de recursos permitidos.

Ejemplo:

```python
MANAGED_SERVICES = {
    "docker": {
        "unit": "docker.service",
        "actions": {"restart"},
    },
    "smbd": {
        "unit": "smbd.service",
        "actions": {"start", "stop", "restart"},
    },
}
```

Un servicio no administrado puede visualizarse, pero no modificarse.

---

## Desarrollo

### Backend

```bash
docker compose up -d
```

Estado:

```bash
docker compose ps
```

Tests:

```bash
make test
```

Tests de integración:

```bash
make test-integration
```

### Host Agent

```bash
sudo systemctl restart serverhub-agent
```

Estado:

```bash
systemctl status serverhub-agent --no-pager
```

Logs:

```bash
journalctl -u serverhub-agent -n 100 --no-pager
```

### Frontend

```bash
cd apps/web
```

Si Node se administra mediante NVM:

```bash
source ~/.bashrc
nvm use --lts
```

Servidor de desarrollo:

```bash
npm run dev -- --host 0.0.0.0
```

Build:

```bash
npm run build
```

Lint:

```bash
npm run lint
```

---

## Mapa de dependencias

ServerHub incluye un generador de mapa de dependencias entre archivos e infraestructura.

```bash
make map
```

Genera:

```text
serverhub-global.dot
serverhub-global.svg
```

El gráfico muestra:

- imports Python;
- relación API → Agent;
- acceso a PostgreSQL;
- Docker;
- systemd;
- discos;
- tests.

---

## Testing

Estado actual documentado:

```text
19 tests backend
```

Incluye:

- health
- CRUD
- estado del sistema
- discos
- servicios
- Docker
- errores 403/404
- stats
- integración real API → Agent → Host

---

## Roadmap

### Sprint 0 — Infraestructura

✅ Completado.

### Sprint 1 — Plataforma base

✅ Docker Compose
✅ FastAPI
✅ PostgreSQL
✅ Host Agent
✅ systemd
✅ Docker
✅ discos

Pendiente:

- Nginx
- Redis cuando exista una necesidad real

### Sprint 2 — Aplicación y experiencia

✅ React
✅ Dashboard
✅ Sistema
✅ Servicios
✅ Discos
✅ Docker monitoring
✅ acciones controladas

Pendiente:

- autenticación
- usuarios
- roles

### Sprint 3 — DevOps

Parcialmente adelantado:

✅ testing
✅ integración
✅ build/lint
✅ Git workflow
✅ mapa de dependencias

Pendiente:

- GitHub Actions
- CI/CD
- backups
- despliegue

### Sprint 4 — Operación

Parcialmente adelantado:

✅ métricas instantáneas
✅ Docker stats
✅ systemd
✅ discos

Pendiente:

- logs
- métricas históricas
- Prometheus
- Grafana
- alertas

### Sprint 5 — Automatización e IA

Pendiente.

---

## Filosofía del proyecto

ServerHub se desarrolla siguiendo un ciclo incremental:

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

El objetivo no es solamente construir una herramienta funcional, sino también utilizar el proyecto como entorno práctico para comprender cómo se conectan distintas tecnologías modernas.

---

## Estado del proyecto

**En desarrollo activo.**

El siguiente hito será revisar y consolidar la arquitectura actual antes de incorporar nuevas capas como autenticación, Nginx o CI/CD.

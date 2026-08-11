import { useEffect, useMemo, useState } from "react";
import {
  getServices,
  restartService,
} from "../services/api";
import type { SystemService } from "../types/serverhub";

type Filter =
  | "all"
  | "active"
  | "inactive"
  | "managed";

const MANAGED_SERVICES = new Set([
  "docker",
  "smbd",
]);

function Services() {
  const [services, setServices] = useState<SystemService[]>([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<Filter>("all");

  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [restarting, setRestarting] =
    useState<string | null>(null);

  async function loadServices() {
    try {
      const data = await getServices();

      setServices(data.services);
      setError(null);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Error desconocido");
      }
    }
  }

  useEffect(() => {
    loadServices();

    const interval = window.setInterval(() => {
      loadServices();
    }, 10000);

    return () => {
      window.clearInterval(interval);
    };
  }, []);

  const activeCount = useMemo(
    () =>
      services.filter(
        (service) => service.active === "active",
      ).length,
    [services],
  );

  const inactiveCount = useMemo(
    () =>
      services.filter(
        (service) => service.active === "inactive",
      ).length,
    [services],
  );

  const managedCount = useMemo(
    () =>
      services.filter((service) =>
        MANAGED_SERVICES.has(service.name),
      ).length,
    [services],
  );

  const filteredServices = useMemo(() => {
    const value = search.toLowerCase().trim();

    return services.filter((service) => {
      const matchesSearch =
        !value ||
        service.name.toLowerCase().includes(value) ||
        service.unit.toLowerCase().includes(value) ||
        service.description.toLowerCase().includes(value) ||
        service.active.toLowerCase().includes(value) ||
        service.sub.toLowerCase().includes(value);

      if (!matchesSearch) {
        return false;
      }

      if (filter === "active") {
        return service.active === "active";
      }

      if (filter === "inactive") {
        return service.active === "inactive";
      }

      if (filter === "managed") {
        return MANAGED_SERVICES.has(service.name);
      }

      return true;
    });
  }, [services, search, filter]);

  async function handleRestart(name: string) {
    if (!MANAGED_SERVICES.has(name)) {
      return;
    }

    const confirmed = window.confirm(
      `¿Reiniciar el servicio ${name}?`,
    );

    if (!confirmed) {
      return;
    }

    setRestarting(name);
    setMessage(null);

    try {
      await restartService(name);

      setMessage(
        `${name} reiniciado correctamente`,
      );

      window.setTimeout(() => {
        loadServices();
      }, 1000);
    } catch (err) {
      if (err instanceof Error) {
        setMessage(err.message);
      } else {
        setMessage("Error desconocido");
      }
    } finally {
      setRestarting(null);
    }
  }

  return (
    <>
      <header className="topbar">
        <div>
          <h1>Servicios</h1>
          <p>Servicios systemd del servidor</p>
        </div>
      </header>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {message && (
        <div className="action-message">
          {message}
        </div>
      )}

      <section className="service-summary">
        <article>
          <span>Total</span>
          <strong>{services.length}</strong>
        </article>

        <article>
          <span>Activos</span>
          <strong>{activeCount}</strong>
        </article>

        <article>
          <span>Inactivos</span>
          <strong>{inactiveCount}</strong>
        </article>

        <article>
          <span>Administrables</span>
          <strong>{managedCount}</strong>
        </article>
      </section>

      <section className="services-toolbar">
        <div className="service-filters">
          <button
            type="button"
            className={filter === "all" ? "selected" : ""}
            onClick={() => setFilter("all")}
          >
            Todos
          </button>

          <button
            type="button"
            className={filter === "active" ? "selected" : ""}
            onClick={() => setFilter("active")}
          >
            Activos
          </button>

          <button
            type="button"
            className={filter === "inactive" ? "selected" : ""}
            onClick={() => setFilter("inactive")}
          >
            Inactivos
          </button>

          <button
            type="button"
            className={filter === "managed" ? "selected" : ""}
            onClick={() => setFilter("managed")}
          >
            Administrables
          </button>
        </div>

        <input
          type="search"
          placeholder="Buscar servicio..."
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
        />
      </section>

      <section className="services-panel">
        <div className="services-table-header">
          <span>Servicio</span>
          <span>Estado</span>
          <span>Subestado</span>
          <span>Acciones</span>
        </div>

        {filteredServices.map((service) => {
          const managed =
            MANAGED_SERVICES.has(service.name);

          return (
            <article
              className="service-row"
              key={service.unit}
            >
              <div>
                <strong>{service.name}</strong>
                <small>{service.description}</small>
              </div>

              <div>
                <span
                  className={
                    service.active === "active"
                      ? "service-active"
                      : "service-inactive"
                  }
                >
                  ● {service.active}
                </span>
              </div>

              <div>
                <span>{service.sub}</span>
              </div>

              <div>
                {managed ? (
                  <button
                    type="button"
                    className="restart-button"
                    onClick={() =>
                      handleRestart(service.name)
                    }
                    disabled={
                      restarting === service.name
                    }
                  >
                    {restarting === service.name
                      ? "Reiniciando..."
                      : "Reiniciar"}
                  </button>
                ) : (
                  <span className="read-only">
                    Solo lectura
                  </span>
                )}
              </div>
            </article>
          );
        })}

        {filteredServices.length === 0 && (
          <div className="services-empty">
            No se encontraron servicios.
          </div>
        )}
      </section>
    </>
  );
}

export default Services;

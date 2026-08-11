import { useEffect, useState } from "react";
import {
  getContainersWithStats,
  getSystemStatus,
  restartContainer,
} from "../services/api";
import type {
  ContainerWithStats,
  SystemStatus,
} from "../types/serverhub";

function formatUptime(seconds: number) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) {
    return `${days}d ${hours}h`;
  }

  return `${hours}h ${minutes}m`;
}

function Dashboard() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [containers, setContainers] =
    useState<ContainerWithStats[]>([]);
  const [containerCount, setContainerCount] = useState(0);

  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] =
    useState<string | null>(null);
  const [restarting, setRestarting] =
    useState<string | null>(null);

  async function loadDashboard() {
    try {
      const [systemData, dockerData] = await Promise.all([
        getSystemStatus(),
        getContainersWithStats(),
      ]);

      setStatus(systemData);
      setContainers(dockerData.containers);
      setContainerCount(dockerData.count);
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
    loadDashboard();

    const interval = window.setInterval(() => {
      loadDashboard();
    }, 5000);

    return () => {
      window.clearInterval(interval);
    };
  }, []);

  async function handleRestartContainer(name: string) {
    const confirmed = window.confirm(
      `¿Reiniciar el contenedor ${name}?`,
    );

    if (!confirmed) {
      return;
    }

    setRestarting(name);
    setActionMessage(null);

    try {
      await restartContainer(name);

      setActionMessage(
        `${name} reiniciado correctamente`,
      );

      window.setTimeout(() => {
        loadDashboard();
      }, 1500);
    } catch (err) {
      if (err instanceof Error) {
        setActionMessage(err.message);
      } else {
        setActionMessage("Error desconocido");
      }
    } finally {
      setRestarting(null);
    }
  }

  return (
    <>
      <header className="topbar">
        <div>
          <h1>Dashboard</h1>
          <p>Estado general del servidor</p>
        </div>

        <div className="status-online">
          ● Servidor online
        </div>
      </header>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {actionMessage && (
        <div className="action-message">
          {actionMessage}
        </div>
      )}

      {!status && !error && (
        <div className="loading">
          Cargando información...
        </div>
      )}

      {status && (
        <>
          <section className="server-title">
            <h2>{status.host.hostname}</h2>

            <span>
              {status.host.cpu.physical_cores} núcleos físicos ·{" "}
              {status.host.cpu.logical_cores} lógicos
            </span>
          </section>

          <section className="metrics">
            <article className="card">
              <span>CPU</span>
              <strong>{status.host.cpu.percent}%</strong>
            </article>

            <article className="card">
              <span>RAM</span>

              <strong>
                {status.host.memory.percent}%
              </strong>

              <small>
                {status.host.memory.used_gb} /{" "}
                {status.host.memory.total_gb} GB
              </small>
            </article>

            <article className="card">
              <span>Disco /</span>

              <strong>
                {status.host.disk.percent}%
              </strong>

              <small>
                {status.host.disk.free_gb} GB libres
              </small>
            </article>

            <article className="card">
              <span>Uptime</span>

              <strong>
                {formatUptime(
                  status.host.uptime_seconds,
                )}
              </strong>
            </article>
          </section>

          <section className="dashboard-grid">
            <section className="details">
              <h3>Memoria swap</h3>

              <div className="detail-row">
                <span>Uso</span>
                <strong>
                  {status.host.swap.percent}%
                </strong>
              </div>

              <div className="detail-row">
                <span>Total</span>
                <strong>
                  {status.host.swap.total_gb} GB
                </strong>
              </div>

              <div className="detail-row">
                <span>Libre</span>
                <strong>
                  {status.host.swap.free_gb} GB
                </strong>
              </div>
            </section>

            <section className="docker-panel">
              <div className="section-heading">
                <div>
                  <h3>Docker</h3>

                  <p>
                    {containerCount}{" "}
                    {containerCount === 1
                      ? "contenedor"
                      : "contenedores"}
                  </p>
                </div>
              </div>

              <div className="containers">
                {containers.map((container) => (
                  <article
                    className="container-card"
                    key={container.id}
                  >
                    <div className="container-header">
                      <div>
                        <strong>
                          {container.name}
                        </strong>

                        <small>
                          {container.image}
                        </small>
                      </div>

                      <div className="container-actions">
                        <span
                          className={
                            container.state === "running"
                              ? "container-running"
                              : "container-stopped"
                          }
                        >
                          ● {container.state}
                        </span>

                        <button
                          type="button"
                          className="restart-button"
                          onClick={() =>
                            handleRestartContainer(
                              container.name,
                            )
                          }
                          disabled={
                            restarting === container.name
                          }
                        >
                          {restarting === container.name
                            ? "Reiniciando..."
                            : "Reiniciar"}
                        </button>
                      </div>
                    </div>

                    {container.stats && (
                      <div className="container-stats">
                        <div>
                          <span>CPU</span>

                          <strong>
                            {
                              container.stats
                                .cpu_percent
                            }
                            %
                          </strong>
                        </div>

                        <div>
                          <span>RAM</span>

                          <strong>
                            {
                              container.stats
                                .memory.percent
                            }
                            %
                          </strong>

                          <small>
                            {
                              container.stats
                                .memory.usage
                            }
                          </small>
                        </div>

                        <div>
                          <span>PIDs</span>

                          <strong>
                            {container.stats.pids}
                          </strong>
                        </div>
                      </div>
                    )}
                  </article>
                ))}
              </div>
            </section>
          </section>
        </>
      )}
    </>
  );
}

export default Dashboard;

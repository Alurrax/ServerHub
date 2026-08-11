import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://192.168.1.9:8000";

type SystemStatus = {
  host: {
    hostname: string;
    cpu: {
      percent: number;
      logical_cores: number;
      physical_cores: number;
    };
    memory: {
      total_gb: number;
      used_gb: number;
      available_gb: number;
      percent: number;
    };
    swap: {
      total_gb: number;
      used_gb: number;
      free_gb: number;
      percent: number;
    };
    disk: {
      mount: string;
      total_gb: number;
      used_gb: number;
      free_gb: number;
      percent: number;
    };
    uptime_seconds: number;
  };
};

type DockerContainer = {
  id: string;
  name: string;
  image: string;
  status: string;
  state: string;
};

type DockerContainersResponse = {
  containers: DockerContainer[];
  count: number;
};

type DockerStats = {
  name: string;
  cpu_percent: number;
  memory: {
    usage: string;
    limit: string;
    percent: number;
  };
  network_io: string;
  block_io: string;
  pids: number;
};

type ContainerWithStats = DockerContainer & {
  stats?: DockerStats;
};

function formatUptime(seconds: number) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) {
    return `${days}d ${hours}h`;
  }

  return `${hours}h ${minutes}m`;
}

function App() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [containers, setContainers] = useState<ContainerWithStats[]>([]);
  const [containerCount, setContainerCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const statusResponse = await fetch(`${API_URL}/system/status`);

        if (!statusResponse.ok) {
          throw new Error("No se pudo obtener el estado del servidor");
        }

        const statusData: SystemStatus = await statusResponse.json();
        setStatus(statusData);

        const containersResponse = await fetch(
          `${API_URL}/system/docker/containers`,
        );

        if (!containersResponse.ok) {
          throw new Error("No se pudo obtener información de Docker");
        }

        const containersData: DockerContainersResponse =
          await containersResponse.json();

          setContainerCount(containersData.count);

        const containersWithStats = await Promise.all(
          containersData.containers.map(async (container) => {
            if (container.state !== "running") {
              return container;
            }

            try {
              const statsResponse = await fetch(
                `${API_URL}/system/docker/containers/${container.name}/stats`,
              );

              if (!statsResponse.ok) {
                return container;
              }

              const stats: DockerStats = await statsResponse.json();

              return {
                ...container,
                stats,
              };
            } catch {
              return container;
            }
          }),
        );

        setContainers(containersWithStats);
        setError(null);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Error desconocido");
        }
      }
    }

        loadDashboard();

    const interval = window.setInterval(() => {
      loadDashboard();
    }, 5000);

    return () => {
      window.clearInterval(interval);
    };
  }, []);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">ServerHub</div>

        <nav>
          <a className="active">Dashboard</a>
          <a>Sistema</a>
          <a>Docker</a>
          <a>Servicios</a>
          <a>Discos</a>
        </nav>
      </aside>

      <main className="content">
        <header className="topbar">
          <div>
            <h1>Dashboard</h1>
            <p>Estado general del servidor</p>
          </div>

          <div className="status-online">● Servidor online</div>
        </header>

        {error && <div className="error">{error}</div>}

        {!status && !error && (
          <div className="loading">Cargando información...</div>
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
                <strong>{status.host.memory.percent}%</strong>
                <small>
                  {status.host.memory.used_gb} /{" "}
                  {status.host.memory.total_gb} GB
                </small>
              </article>

              <article className="card">
                <span>Disco /</span>
                <strong>{status.host.disk.percent}%</strong>
                <small>{status.host.disk.free_gb} GB libres</small>
              </article>

              <article className="card">
                <span>Uptime</span>
                <strong>{formatUptime(status.host.uptime_seconds)}</strong>
              </article>
            </section>

            <section className="dashboard-grid">
              <section className="details">
                <h3>Memoria swap</h3>

                <div className="detail-row">
                  <span>Uso</span>
                  <strong>{status.host.swap.percent}%</strong>
                </div>

                <div className="detail-row">
                  <span>Total</span>
                  <strong>{status.host.swap.total_gb} GB</strong>
                </div>

                <div className="detail-row">
                  <span>Libre</span>
                  <strong>{status.host.swap.free_gb} GB</strong>
                </div>
              </section>

              <section className="docker-panel">
                <div className="section-heading">
                  <div>
                    <h3>Docker</h3>
                    <p>{containerCount} contenedores</p>
                  </div>
                </div>

                <div className="containers">
                  {containers.map((container) => (
                    <article className="container-card" key={container.id}>
                      <div className="container-header">
                        <div>
                          <strong>{container.name}</strong>
                          <small>{container.image}</small>
                        </div>

                        <span
                          className={
                            container.state === "running"
                              ? "container-running"
                              : "container-stopped"
                          }
                        >
                          ● {container.state}
                        </span>
                      </div>

                      {container.stats && (
                        <div className="container-stats">
                          <div>
                            <span>CPU</span>
                            <strong>{container.stats.cpu_percent}%</strong>
                          </div>

                          <div>
                            <span>RAM</span>
                            <strong>
                              {container.stats.memory.percent}%
                            </strong>
                            <small>{container.stats.memory.usage}</small>
                          </div>

                          <div>
                            <span>PIDs</span>
                            <strong>{container.stats.pids}</strong>
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
      </main>
    </div>
  );
}

export default App;

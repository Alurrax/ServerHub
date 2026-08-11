import { useEffect, useState } from "react";
import "./App.css";

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

function formatUptime(seconds: number) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  return `${hours}h ${minutes}m`;
}

function App() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://192.168.1.9:8000/system/status")
      .then((response) => {
        if (!response.ok) {
          throw new Error("No se pudo obtener el estado del servidor");
        }

        return response.json();
      })
      .then((data) => {
        setStatus(data);
      })
      .catch((err) => {
        setError(err.message);
      });
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
          </>
        )}
      </main>
    </div>
  );
}

export default App;

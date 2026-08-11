import { useEffect, useState } from "react";
import { getSystemStatus } from "../services/api";
import type { SystemStatus } from "../types/serverhub";

function formatUptime(seconds: number) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  return `${days}d ${hours}h ${minutes}m`;
}

function System() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadSystem() {
    try {
      const data = await getSystemStatus();

      setStatus(data);
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
    loadSystem();

    const interval = window.setInterval(() => {
      loadSystem();
    }, 5000);

    return () => {
      window.clearInterval(interval);
    };
  }, []);

  return (
    <>
      <header className="topbar">
        <div>
          <h1>Sistema</h1>
          <p>Información del host Ubuntu</p>
        </div>

        <div className="status-online">
          ● Actualización cada 5 segundos
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      {!status && !error && (
        <div className="loading">
          Cargando información del sistema...
        </div>
      )}

      {status && (
        <>
          <section className="system-header-card">
            <div>
              <span>Servidor</span>
              <h2>{status.host.hostname}</h2>
            </div>

            <div>
              <span>Uptime</span>
              <strong>
                {formatUptime(status.host.uptime_seconds)}
              </strong>
            </div>
          </section>

          <section className="system-sections">
            <article className="system-panel">
              <h3>Procesador</h3>

              <div className="system-main-value">
                {status.host.cpu.percent}%
              </div>

              <div className="system-row">
                <span>Núcleos físicos</span>
                <strong>
                  {status.host.cpu.physical_cores}
                </strong>
              </div>

              <div className="system-row">
                <span>Núcleos lógicos</span>
                <strong>
                  {status.host.cpu.logical_cores}
                </strong>
              </div>

              <div className="system-row">
                <span>Load 1 min</span>
                <strong>{status.host.cpu.load_1m}</strong>
              </div>

              <div className="system-row">
                <span>Load 5 min</span>
                <strong>{status.host.cpu.load_5m}</strong>
              </div>

              <div className="system-row">
                <span>Load 15 min</span>
                <strong>{status.host.cpu.load_15m}</strong>
              </div>
            </article>

            <article className="system-panel">
              <h3>Memoria RAM</h3>

              <div className="system-main-value">
                {status.host.memory.percent}%
              </div>

              <div className="system-row">
                <span>Total</span>
                <strong>
                  {status.host.memory.total_gb} GB
                </strong>
              </div>

              <div className="system-row">
                <span>Usada</span>
                <strong>
                  {status.host.memory.used_gb} GB
                </strong>
              </div>

              <div className="system-row">
                <span>Disponible</span>
                <strong>
                  {status.host.memory.available_gb} GB
                </strong>
              </div>
            </article>

            <article className="system-panel">
              <h3>Swap</h3>

              <div className="system-main-value">
                {status.host.swap.percent}%
              </div>

              <div className="system-row">
                <span>Total</span>
                <strong>
                  {status.host.swap.total_gb} GB
                </strong>
              </div>

              <div className="system-row">
                <span>Usada</span>
                <strong>
                  {status.host.swap.used_gb} GB
                </strong>
              </div>

              <div className="system-row">
                <span>Libre</span>
                <strong>
                  {status.host.swap.free_gb} GB
                </strong>
              </div>
            </article>

            <article className="system-panel">
              <h3>Sistema de archivos raíz</h3>

              <div className="system-main-value">
                {status.host.disk.percent}%
              </div>

              <div className="system-row">
                <span>Montaje</span>
                <strong>{status.host.disk.mount}</strong>
              </div>

              <div className="system-row">
                <span>Total</span>
                <strong>
                  {status.host.disk.total_gb} GB
                </strong>
              </div>

              <div className="system-row">
                <span>Usado</span>
                <strong>
                  {status.host.disk.used_gb} GB
                </strong>
              </div>

              <div className="system-row">
                <span>Libre</span>
                <strong>
                  {status.host.disk.free_gb} GB
                </strong>
              </div>
            </article>
          </section>
        </>
      )}
    </>
  );
}

export default System;

import { useEffect, useState } from "react";
import { getDisks } from "../services/api";
import type { Disk } from "../types/serverhub";

function Disks() {
  const [disks, setDisks] = useState<Disk[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadDisks() {
    try {
      const data = await getDisks();

      setDisks(data.disks);
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
    loadDisks();
  }, []);

  return (
    <>
      <header className="topbar">
        <div>
          <h1>Discos</h1>
          <p>Almacenamiento físico y particiones del servidor</p>
        </div>
      </header>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {!error && disks.length === 0 && (
        <div className="loading">
          Cargando discos...
        </div>
      )}

      <section className="disks-grid">
        {disks.map((disk) => (
          <article
            className="disk-card"
            key={disk.path}
          >
            <div className="disk-header">
              <div>
                <span>Disco</span>
                <h2>{disk.name}</h2>
                <small>{disk.path}</small>
              </div>

              <strong>
                {disk.size_gib} GiB
              </strong>
            </div>

            <div className="partitions">
              {disk.partitions.map((partition) => (
                <div
                  className="partition-row"
                  key={partition.path}
                >
                  <div className="partition-main">
                    <strong>
                      {partition.name}
                    </strong>

                    <small>
                      {partition.path}
                    </small>
                  </div>

                  <div>
                    <span>Filesystem</span>
                    <strong>
                      {partition.filesystem ?? "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Etiqueta</span>
                    <strong>
                      {partition.label ?? "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Tamaño</span>
                    <strong>
                      {partition.size_gib} GiB
                    </strong>
                  </div>

                  <div>
                    <span>Uso</span>
                    <strong>
                      {partition.used_percent ?? "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Disponible</span>
                    <strong>
                      {partition.available_gib !== null
                        ? `${partition.available_gib} GiB`
                        : "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Montaje</span>
                    <strong>
                      {partition.mountpoints.length > 0
                        ? partition.mountpoints.join(", ")
                        : "—"}
                    </strong>
                  </div>
                </div>
              ))}
            </div>
          </article>
        ))}
      </section>
    </>
  );
}

export default Disks;

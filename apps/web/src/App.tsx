import { useState } from "react";
import "./App.css";

import Sidebar from "./components/Sidebar";
import type { Page } from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Services from "./pages/Services";

function App() {
  const [currentPage, setCurrentPage] =
    useState<Page>("dashboard");

  return (
    <div className="app">
      <Sidebar
        currentPage={currentPage}
        onNavigate={setCurrentPage}
      />

      <main className="content">
        {currentPage === "dashboard" && (
          <Dashboard />
        )}

        {currentPage === "system" && (
          <div>
            <h1>Sistema</h1>
            <p>Próximamente.</p>
          </div>
        )}

        {currentPage === "docker" && (
          <div>
            <h1>Docker</h1>
            <p>Próximamente.</p>
          </div>
        )}

        {currentPage === "services" && (
           <Services />
        )}

        {currentPage === "disks" && (
          <div>
            <h1>Discos</h1>
            <p>Próximamente.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

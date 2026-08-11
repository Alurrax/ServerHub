export type Page =
  | "dashboard"
  | "system"
  | "docker"
  | "services"
  | "disks";

type SidebarProps = {
  currentPage: Page;
  onNavigate: (page: Page) => void;
};

function Sidebar({
  currentPage,
  onNavigate,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="logo">
        ServerHub
      </div>

      <nav>
        <button
          className={
            currentPage === "dashboard"
              ? "nav-item active"
              : "nav-item"
          }
          onClick={() => onNavigate("dashboard")}
        >
          Dashboard
        </button>

        <button
          className={
            currentPage === "system"
              ? "nav-item active"
              : "nav-item"
          }
          onClick={() => onNavigate("system")}
        >
          Sistema
        </button>

        <button
          className={
            currentPage === "docker"
              ? "nav-item active"
              : "nav-item"
          }
          onClick={() => onNavigate("docker")}
        >
          Docker
        </button>

        <button
          className={
            currentPage === "services"
              ? "nav-item active"
              : "nav-item"
          }
          onClick={() => onNavigate("services")}
        >
          Servicios
        </button>

        <button
          className={
            currentPage === "disks"
              ? "nav-item active"
              : "nav-item"
          }
          onClick={() => onNavigate("disks")}
        >
          Discos
        </button>
      </nav>
    </aside>
  );
}

export default Sidebar;

import { NavLink, Outlet, useParams } from "react-router-dom";

export default function Projects() {
  const { title } = localStorage.getItem("current_project_title");

  return (
    <div className="flex min-h-screen bg-[#111] text-white font-mono">
      {/* Sidebar */}
      <aside className="w-60 p-4 bg-[#1a1a1a] border-r border-gray-800 flex flex-col space-y-4">
        <h2 className="text-xl font-bold text-center mb-4 text-size:2">🎬 {title} </h2>

        <NavButton to="screenplay" label="Screenplay" icon="🎬" />
        <NavButton to="visualization" label="Visualization" icon="🎨" />
        <NavButton to="budget" label="Budget" icon="💰" />
        <NavButton to="scheduling" label="Scheduling" icon="🕒" />
        <NavButton to="edit" label="Edit Project" icon="✏️" />
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}

// Reusable NavLink-style button
function NavButton({ to, label, icon }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `block px-4 py-2 rounded-lg transition font-medium text-left ${
          isActive
            ? "bg-blue-600 text-white"
            : "bg-[#222] text-gray-300 hover:bg-blue-700 hover:text-white"
        }`
      }
    >
      {icon} {label}
    </NavLink>
  );
}

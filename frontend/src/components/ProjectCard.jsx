import { useNavigate, Link } from "react-router-dom";

export default function ProjectCard({ project }) {
  const navigate = useNavigate();

  return (
    <div className="relative w-64 m-4 shadow-xl rounded-lg overflow-hidden border border-black bg-[#222] text-white font-mono">
      {/* Three-dot menu for edit/delete */}
      <div className="absolute top-2 right-2 z-10">
        <button
          className="text-white hover:text-gray-400 focus:outline-none"
          onClick={(e) => {
            e.stopPropagation(); // ✅ prevents Link click from firing
            navigate(`/projects/${project.project_id}/edit`);
          }}
        >
          <svg
            className="w-6 h-6"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zm6-2a2 2 0 100 4 2 2 0 000-4zm4-2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </button>
      </div>

      <Link
        to={`/projects/${project.project_id}`}
        onClick={() => {
          localStorage.setItem("current_project_id", project.project_id);
          localStorage.setItem("current_project_title", project.title);
        }}

        className="no-underline hover:shadow-lg transition-shadow duration-300 block"
      >
        {/* Top Clapper */}
        <div className="bg-gradient-to-r from-white to-black flex justify-between items-center px-2 py-1 border-b-2 border-black">
          <div className="w-6 h-4 bg-black rotate-[-10deg]"></div>
          <div className="w-6 h-4 bg-white rotate-[10deg]"></div>
          <div className="w-6 h-4 bg-black rotate-[-10deg]"></div>
          <div className="w-6 h-4 bg-white rotate-[10deg]"></div>
        </div>

        {/* Hinge separator */}
        <div className="h-2 bg-black"></div>

        {/* Main body */}
        <div className="p-4 bg-[#1a1a1a] flex flex-col justify-between h-48">
          <h2 className="text-lg font-bold uppercase text-center border-b border-white pb-1">
            {project.title}
          </h2>
          <div className="text-sm mt-2 space-y-1">
            <p>
              <span className="text-gray-400">Director:</span> {project.director}
            </p>
            <p>
              <span className="text-gray-400">Producer:</span> {project.producer}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              🎬 Created: {project.createdat}
            </p>
          </div>
        </div>
      </Link>
    </div>
  );
}


// pages/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import ProjectCard from '../components/project_card';

const Projects = () => {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    // Simulated API call
    setProjects([
      {
        id: 1,
        name: "The Shadows",
        director: "Zayn Mady",
        producer: "Nour Khaled",
        createdAt: "2025-06-01",
      },
      {
        id: 2,
        name: "Fragments",
        director: "Layla Hussein",
        producer: "Zayn Mady",
        createdAt: "2025-07-03",
      },
    ]);
  }, []);

  return (
    <div
      className="min-h-screen bg-cover bg-center p-8"
      style={{ backgroundImage: "url('/whiteboard.jpg')" }}
    >
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-black drop-shadow-lg">🎬 My Projects</h1>
        <button className="bg-black text-white px-4 py-2 rounded-lg shadow hover:bg-gray-800 transition">
          + Create New Project
        </button>
      </div>

      <div className="flex flex-wrap justify-start">
        {projects.map(project => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
    </div>
  );
};

export default Projects;


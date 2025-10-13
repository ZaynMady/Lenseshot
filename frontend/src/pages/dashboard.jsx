import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ProjectCard from '../components/ProjectCard';
import CreateProjectModal from '../components/CreateProjectModal';
import {createClient} from '@supabase/supabase-js'


const Dashboard = () => {
  const [projects, setProjects] = useState([]);
  const [showModal, setShowModal] = useState(false);
    const supabaseUrl = import.meta.env.VITE_SUPABASE_PROJECT_URL;
    const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;
    const supabase = createClient(supabaseUrl, supabaseKey);

  const fetchProjects = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const access_token = session?.access_token
      const res = await axios.get("http://localhost:7000/api/projects/list", {
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      });
      setProjects(res.data);
    } catch (err) {
      console.error("Error fetching projects:", err);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleProjectCreated = () => {
    setShowModal(false);
    fetchProjects();
  };

  return (
    <div className="min-h-screen bg-cover bg-center p-8" style={{ backgroundImage: "url('/whiteboard.jpg')" }}>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-black drop-shadow-lg">🎬 My Projects</h1>
        <button
          onClick={() => setShowModal(true)}
          className="bg-black text-white px-4 py-2 rounded-lg shadow hover:bg-gray-800 transition"
        >
          + Create New Project
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {projects.map((project) => (
          <ProjectCard key={project.project_id} project={project} />
        ))}
      </div>

      {showModal && (
        <CreateProjectModal onClose={() => setShowModal(false)} onSuccess={handleProjectCreated} />
      )}
    </div>
  );
};

export default Dashboard;

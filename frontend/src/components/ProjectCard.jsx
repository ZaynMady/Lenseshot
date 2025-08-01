// components/ProjectCard.jsx
import React from 'react';

const ProjectCard = ({ project }) => {
  return (
    <div className="w-64 m-4 shadow-xl rounded-lg overflow-hidden border border-black bg-[#222] text-white font-mono">
      {/* Top Clapper (stripes) */}
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
        <h2 className="text-lg font-bold uppercase text-center border-b border-white pb-1">{project.name}</h2>
        <div className="text-sm mt-2 space-y-1">
          <p><span className="text-gray-400">Director:</span> {project.director}</p>
          <p><span className="text-gray-400">Producer:</span> {project.producer}</p>
          <p className="text-xs text-gray-500 mt-2">🎬 Created: {project.createdAt}</p>
        </div>
      </div>
    </div>
  );
};

export default ProjectCard;

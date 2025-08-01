import React, { useState } from 'react';
import axios from 'axios';

const CreateProjectModal = ({ onClose, onSuccess }) => {
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [error, setError] = useState('');

  const handleCreate = async () => {
    if (!name.trim()) {
      setError('Project name is required.');
      return;
    }

    try {
      await axios.post(
        "http://localhost:5000/api/create_project",
        { metadata: { name, description: desc } },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );
      setName('');
      setDesc('');
      setError('');
      onSuccess();
      onClose(); // Optional: close modal on success
    } catch (err) {
      setError(err.response?.data?.message || 'Error creating project.');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4 text-center">🎬 Create New Project</h2>
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Project Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border px-4 py-2 rounded focus:outline-none placeholder-gray-500"
          />
          <textarea
            placeholder="Project Description"
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            className="w-full border px-4 py-2 rounded focus:outline-none resize-none placeholder-gray-500"
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
        </div>
        <div className="flex justify-end gap-3 mt-4">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded border text-black border-gray-400 hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800"
          >
            Create
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateProjectModal;

import React, { useState } from 'react';
import axios from 'axios';
import { XCircle, Film, User, AlignLeft, Calendar, Tag } from "lucide-react";


const CreateProjectModal = ({ onClose, onSuccess }) => {
const [formData, setFormData] = useState({
    title: "",
    producer: "",
    description: "",
    due_date: "",
    genre: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreate = async () => {
    const { title, producer } = formData;

    if (!title.trim() || !producer.trim()) {
      setError("Project title and producer are required.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await axios.post(
        "http://localhost:7000/api/projects/create",
        {
          metadata: formData,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );
      onSuccess?.();
      onClose?.();
    } catch (err) {
      setError(err.response?.data?.message || "Error creating project.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-[#1e1e1e] text-white rounded-2xl shadow-2xl w-full max-w-lg p-8 relative animate-fadeIn">
        {/* Header */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition"
        >
          <XCircle size={22} />
        </button>

        <h2 className="text-2xl font-bold text-center mb-6">🎬 Create New Project</h2>

        {/* Inputs */}
        <div className="space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">
              Project Title
            </label>
            <div className="flex items-center border border-gray-600 rounded-lg bg-[#2a2a2a] px-3">
              <Film size={18} className="text-gray-400 mr-2" />
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Enter project title"
                className="w-full bg-transparent py-2 text-white placeholder-gray-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Producer */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">
              Producer
            </label>
            <div className="flex items-center border border-gray-600 rounded-lg bg-[#2a2a2a] px-3">
              <User size={18} className="text-gray-400 mr-2" />
              <input
                type="text"
                name="producer"
                value={formData.producer}
                onChange={handleChange}
                placeholder="Enter producer name"
                className="w-full bg-transparent py-2 text-white placeholder-gray-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">
              Description
            </label>
            <div className="flex items-start border border-gray-600 rounded-lg bg-[#2a2a2a] px-3">
              <AlignLeft size={18} className="text-gray-400 mt-2 mr-2" />
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows="3"
                placeholder="Short description of your project"
                className="w-full bg-transparent py-2 text-white placeholder-gray-500 focus:outline-none resize-none"
              />
            </div>
          </div>

          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">
              Due Date
            </label>
            <div className="flex items-center border border-gray-600 rounded-lg bg-[#2a2a2a] px-3">
              <Calendar size={18} className="text-gray-400 mr-2" />
              <input
                type="date"
                name="due_date"
                value={formData.due_date}
                onChange={handleChange}
                className="w-full bg-transparent py-2 text-white placeholder-gray-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Genre */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">
              Genre
            </label>
            <div className="flex items-center border border-gray-600 rounded-lg bg-[#2a2a2a] px-3">
              <Tag size={18} className="text-gray-400 mr-2" />
              <input
                type="text"
                name="genre"
                value={formData.genre}
                onChange={handleChange}
                placeholder="e.g. Drama, Horror, Sci-Fi"
                className="w-full bg-transparent py-2 text-white placeholder-gray-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Error */}
          {error && (
            <p className="text-red-400 text-sm mt-2 text-center">{error}</p>
          )}
        </div>

        {/* Buttons */}
        <div className="flex justify-end gap-3 mt-8">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-700 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            disabled={loading}
            className={`px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 transition text-white font-medium ${
              loading ? "opacity-60 cursor-not-allowed" : ""
            }`}
          >
            {loading ? "Creating..." : "Create Project"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateProjectModal;

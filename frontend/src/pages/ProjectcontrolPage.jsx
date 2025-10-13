import React, { useEffect, useState } from "react";
import { Plus, Save, Trash2 } from "lucide-react";
import axios from "axios";
import {createClient} from '@supabase/supabase-js'

export default function ProjectControlPage({ }) {
  const supabaseUrl = import.meta.env.VITE_SUPABASE_PROJECT_URL;
  const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;  
  const supabase = createClient(supabaseUrl, supabaseKey);
  const [metadata, setMetadata] = useState({});
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");
  const projectId = localStorage.getItem("current_project_id");

  // ✅ Load metadata
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        const access_token = session?.access_token
        const res = await fetch(`http://localhost:7000/api/projects/${projectId}/metadata`, {
          headers: { "Authorization": `Bearer ${access_token}`, 
         "Content-Type": "application/json" }
        });
        if (!res.ok) throw new Error("Failed to fetch metadata");
        const data = await res.json();
        setMetadata(data);
      } catch (err) {
        console.error(err);
        setMessage("❌ Error loading project metadata");
      } finally {
        setLoading(false);
      }
    };
    fetchMetadata();
  }, [projectId]);

  // ✅ Handle field changes
  const handleChange = (key, value) => {
    setMetadata((prev) => ({ ...prev, [key]: value }));
  };

  // ✅ Add new metadata field
  const handleAddField = () => {
    if (!newKey.trim()) return;
    setMetadata((prev) => ({ ...prev, [newKey]: newValue }));
    setNewKey("");
    setNewValue("");
  };

  // ✅ Save metadata
  const handleSave = async () => {
    setMessage("");
    try {
        const { data: { session } } = await supabase.auth.getSession()
        const access_token = session?.access_token
        const res =  await axios.put(`http://localhost:7000/api/projects/${projectId}/metadata`, { metadata }, {
            headers: {
              Authorization: `Bearer ${access_token}`,
            },
          });
      setMessage("✅ Project metadata saved successfully!");
    } catch (err) {
      console.error(err);
      setMessage("❌ Error saving metadata");
    }
  };

  // ✅ Delete project
  const handleDelete = async () => {
    if (!window.confirm("⚠️ Are you sure you want to delete this project?")) return;
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const access_token = session?.access_token
      const res = await fetch(`http://localhost:7000/api/projects/${projectId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${access_token}`,
          "Content-Type": "application/json"
        }
      });
      if (!res.ok) throw new Error("Failed to delete project");
      setMessage("🗑️ Project deleted successfully!");
      setTimeout(() => (window.location.href = "/projects"), 1200);
    } catch (err) {
      console.error(err);
      setMessage("❌ Error deleting project");
    }
  };

  if (loading)
    return <div className="text-center py-12 text-gray-500">Loading project data...</div>;

  return (
    <div className="max-w-4xl mx-auto mt-12 bg-white shadow-lg rounded-2xl p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center border-b pb-4">
        <h1 className="text-2xl font-semibold text-gray-800">Project Control Panel</h1>
        <button
          onClick={handleDelete}
          className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition"
        >
          <Trash2 size={18} /> Delete Project
        </button>
      </div>

      {/* Metadata Display */}
      <div className="space-y-4">
        {Object.keys(metadata).map((key) => (
          <div key={key} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <label className="text-gray-600 font-medium capitalize">{key}</label>
            <input
              type="text"
              value={metadata[key] ?? ""}
              onChange={(e) => handleChange(key, e.target.value)}
              className="border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 text-gray-800 bg-white"
              placeholder={metadata[key] ?? ""}
            />
          </div>
        ))}
      </div>

      {/* Add New Metadata Field */}
      <div className="pt-4 border-t mt-6 space-y-3">
        <h2 className="text-lg font-semibold text-gray-700">Add New Metadata</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="New field name"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
            className="border border-gray-300 rounded-lg p-2.5 text-gray-800"
          />
          <input
            type="text"
            placeholder="Value"
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
            className="border border-gray-300 rounded-lg p-2.5 text-gray-800"
          />
          <button
            onClick={handleAddField}
            className="flex items-center justify-center gap-2 bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-900 transition"
          >
            <Plus size={16} /> Add Field
          </button>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end pt-6">
        <button
          onClick={handleSave}
          className="flex items-center gap-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          <Save size={18} /> Save Changes
        </button>
      </div>

      {/* Message */}
      {message && (
        <div
          className={`text-center text-sm mt-6 py-2 rounded-lg ${
            message.includes("✅") || message.includes("🗑️")
              ? "bg-green-50 text-green-700"
              : "bg-red-50 text-red-700"
          }`}
        >
          {message}
        </div>
      )}
    </div>
  );
}

import React, { useEffect, useState } from "react";

export default function OpenScreenplayModal({ onOpen, isOpen, onClose }) {
  const [listOfScripts, setListOfScripts] = useState([]);
  const [selectedScript, setSelectedScript] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // ✅ Fetch screenplay list only when modal opens
  useEffect(() => {
    if (!isOpen) return;

    const fetchScripts = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch("http://localhost:8000/api/list_screenplays", {
          method: "POST", 
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            project_id: localStorage.getItem("current_project_id"),
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to load screenplays");
        }

        const data = await response.json();
        // assuming backend returns { screenplays: ["screenplay1", "screenplay2"] }
        setListOfScripts(data.screenplays);
      } catch (err) {
        console.error("Error fetching screenplay list:", err);
        setError("Could not load screenplays.");
      } finally {
        setLoading(false);
      }
    };

    fetchScripts();
  }, [isOpen]);

  const handleOpen = async () => {
    if (!selectedScript) return;
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/open_screenplay", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          screenplay_name: selectedScript + ".xml",
          project_id: localStorage.getItem("current_project_id"),
        }),
      });

      if (!response.ok) throw new Error("Failed to open screenplay");

      const data = await response.json();
      onOpen(data);
    } catch (err) {
      console.error("Error opening screenplay:", err);
      setError("Could not open screenplay.");
    } finally {
      setLoading(false);
      //adding the screenplay name to local storage
      localStorage.setItem("current_screenplay_name", selectedScript + ".xml");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-xl shadow-xl w-96 flex flex-col gap-4">
        <h2 className="text-lg font-semibold text-gray-800">Open Screenplay</h2>

        {loading && listOfScripts.length === 0 && <p>Loading screenplays...</p>}
        {error && <p className="text-red-500 text-sm">{error}</p>}

        <select
          value={selectedScript}
          onChange={(e) => setSelectedScript(e.target.value)}
          className="p-2 border rounded-md"
        >
          <option value="">-- Select a screenplay --</option>
          {listOfScripts.map((title, idx) => (
            <option key={idx} value={title}>
              {title}
            </option>
          ))}
        </select>

        <div className="flex justify-end gap-2 mt-4">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
          <button
            onClick={handleOpen}
            disabled={!selectedScript || loading}
            className={`px-4 py-2 rounded text-white ${
              loading || !selectedScript
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {loading ? "Opening..." : "Open"}
          </button>
        </div>
      </div>
    </div>
  );
}

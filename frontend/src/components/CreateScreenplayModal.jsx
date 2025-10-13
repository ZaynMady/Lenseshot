import { useState } from "react";
import { createClient } from "@supabase/supabase-js"

const CreateScreenplayModal = ({isOpen, onClose}) => {
    const supabaseUrl = import.meta.env.VITE_SUPABASE_PROJECT_URL;
    const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;  
    const supabase = createClient(supabaseUrl, supabaseKey);
    const [title, settitle] = useState('');
    const [template, settemplate] = useState('');
    const [loading, setloading] = useState(false);
    const templates = [
        {value: "american_screenplay.lss", label: "American Screenplay"}, 
        {value: "arabic_screenplay.lss", label: "Arabic Screenplay"}
    ]

    const handleSubmit = async () => {
        if (!title.trim()) {
            return;
        }
    
    setloading(true);
    try {
      const {data : {session}} = await supabase.auth.getSession()
      const access_token = session?.access_token
    const response = await fetch("http://localhost:8000/api/create_screenplay", {
        method: "POST", 
        headers: {
            "content-type": "application/json", 
            "Authorization": `Bearer ${access_token}`
        },
        body: JSON.stringify({
            "template_name": template, 
            "screenplay_name": title, 
            "project_id": localStorage.getItem('current_project_id')


        }),
      });

      if(response.ok){
        settitle('');
        settemplate('');
        onClose(true);
      }
      else {
        console.error("Failed to create screenplay");
      }
    }catch (error) {
        console.error("Error creating screenplay:", error);
      }
      finally {
        setloading(false);
      }
        };

        if (!isOpen) return null;

        return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
      <div className="bg-white rounded-2xl shadow-xl p-6 w-96">
        <h2 className="text-xl font-semibold mb-4">Create Screenplay</h2>

        <input
          type="text"
          placeholder="Enter screenplay name"
          value={title}
          onChange={(e) => settitle(e.target.value)}
          className="w-full border rounded-lg p-2 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
        value={template}
        onChange={(e) => settemplate(e.target.value)}
        className="w-full border rounded-lg p-2 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
        <option value="">-- Select a Template --</option>
        {templates.map((tpl) => (
            <option key={tpl.value} value={tpl.value}>
            {tpl.label}
            </option>
        ))}
        </select>

        <div className="flex justify-end gap-3">
          <button
            onClick={() => onClose(false)}
            className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default CreateScreenplayModal;
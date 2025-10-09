import { useState, useRef } from "react";
import CreateScreenplayModal from "../components/CreateScreenplayModal";
import { useNavigate } from "react-router-dom";
import ScreenplayEditor from "../components/screenplayeditor";
import OpenScreenplayModal from "../components/openscreenplayModal";

export default function Screenplay() {
  const [activeComponent, setActiveComponent] = useState("action");
  const [openMenu, setOpenMenu] = useState(null);
  const [isScreenplayModalOpen, setIsScreenplayModalOpen] = useState(false);
  const [isOpenScreenplayModalOpen, setIsOpenScreenplayModalOpen] = useState(false);
  const [components, setComponents] = useState(["A", "C", "D", "S"]);
  const [screenplayJson, setscreenplayJson] = useState("");
  const [styles, setStyles] = useState("");

  const navigate = useNavigate();

  // ✅ 1. Ref to access editor methods
  const editorRef = useRef(null);

  const menuItems = {
    File: ["New", "Open", "Save", "delete", "Save As", "Export"],
    Edit: ["Undo", "Redo", "Cut", "Copy", "Paste"],
    Tools: ["Spell Check", "Stats", "Auto-Format"],
  };

  // ✅ 2. Save handler that talks to backend
  const handleSave = async () => {
    if (!editorRef.current) return;
    const screenplayData = editorRef.current.getScreenplayData(); // from useImperativeHandle

    try {
      const response = await fetch("http://localhost:8000/api/save_screenplay", {
        method: "POST",
        headers: { "Content-Type": "application/json", 
          "Authorization": `Bearer ${localStorage.getItem('access_token')}`
         },
        body: JSON.stringify({ screenplay: screenplayData
          , project_id: localStorage.getItem("current_project_id")
          , screenplay_name: localStorage.getItem("current_screenplay_name")
         }),
      });

      if (!response.ok) throw new Error("Failed to save screenplay");
      const result = await response.json();
      alert("✅ Screenplay saved successfully!");
    } catch (error) {
      console.error(error);
      alert("❌ Error saving screenplay.");
    }
  };
  // 3. delete handler

  const deleteHandler = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/delete_screenplay", {
        method: "POST",
        headers: { "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem('access_token')}`
       },
        body: JSON.stringify({
         project_id: localStorage.getItem("current_project_id"),
         screenplay_name: localStorage.getItem("current_screenplay_name")
        }),
      });
      if (!response.ok) throw new Error("Failed to delete screenplay");
      const result = await response.json();
      alert("✅ Screenplay deleted successfully!");
      navigate("/projects"); // Redirect to projects page after deletion

    } catch (error) {
      console.error(error);
      alert("❌ Error deleting screenplay.");
    }}  

  return (
    <div className="flex flex-col h-full font-mono text-black relative">
      <style>{styles}</style>

      {/* Toolbar 1: File / Edit / Tools with dropdowns */}
      <div className="flex bg-gray-900 text-white px-4 py-2 space-x-6 border-b border-gray-700 relative z-10">
        {Object.keys(menuItems).map((menu) => (
          <div
            key={menu}
            className="relative"
            onMouseEnter={() => setOpenMenu(menu)}
            onMouseLeave={() => setOpenMenu(null)}
          >
            <button className="hover:text-blue-400">{menu}</button>
            {openMenu === menu && (
              <div className="absolute top-full left-0 bg-[#1a1a1a] border border-gray-700 rounded shadow-lg mt-1 z-20 w-40">
                {menuItems[menu].map((item) => (
                  <div
                    key={item}
                    onClick={() => {
                      if (item === "New") setIsScreenplayModalOpen(true);
                      if (item === "Open") setIsOpenScreenplayModalOpen(true);
                      if (item === "Save") handleSave(); 
                      if (item === "delete") deleteHandler();
                    }}
                    className="px-4 py-2 text-sm hover:bg-blue-600 cursor-pointer"
                  >
                    {item}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Modals */}
      <OpenScreenplayModal
        isOpen={isOpenScreenplayModalOpen}
        onOpen={(data) => {
          setscreenplayJson(data.content);
          setStyles(data.style);
          setComponents(data.components);
          setIsOpenScreenplayModalOpen(false);
        }}
        onClose={() => setIsOpenScreenplayModalOpen(false)}
      />

      <CreateScreenplayModal
        isOpen={isScreenplayModalOpen}
        onClose={() => setIsScreenplayModalOpen(false)}
      />

      {/* Toolbar 2: Component Switcher */}
      <div className="flex bg-gray-800 text-white px-4 py-2 space-x-3 border-b border-gray-600 z-0">
        {components.map((comp) => (
          <button
            key={comp}
            onClick={() => setActiveComponent(comp.toLowerCase())}
            className={`px-3 py-1 rounded ${
              activeComponent === comp.toLowerCase()
                ? "bg-blue-600"
                : "hover:bg-gray-700"
            }`}
          >
            {comp}
          </button>
        ))}
      </div>

      {/* Editor */}
      <div className="flex-grow overflow-auto bg-gray-100">
        <ScreenplayEditor
          ref={editorRef} // ✅ 4. Attach the ref here
          screenplayJson={screenplayJson}
          ActiveComponent={activeComponent}
          setActiveComponent={setActiveComponent}
        />
      </div>
    </div>
  );
}

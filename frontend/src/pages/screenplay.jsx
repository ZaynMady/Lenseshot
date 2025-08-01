import { useState } from "react";

export default function Screenplay() {
  const [activeComponent, setActiveComponent] = useState("action");
  const [openMenu, setOpenMenu] = useState(null);

  const components = ["Action", "Dialogue", "Character", "Shot", "Transition"];

  const menuItems = {
    File: ["New", "Open", "Save", "Save As", "Export"],
    Edit: ["Undo", "Redo", "Cut", "Copy", "Paste"],
    Tools: ["Spell Check", "Stats", "Auto-Format"],
  };

  return (
    <div className="flex flex-col h-full font-mono text-black relative">
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
      <div className="flex-1 bg-white p-6 overflow-y-auto">
        <h2 className="text-gray-500 text-sm mb-2 capitalize">
          {activeComponent} block
        </h2>
        <textarea
          placeholder={`Write ${activeComponent} here...`}
          className="w-full h-full resize-none outline-none text-black text-lg font-serif"
          style={{ minHeight: "400px" }}
        />
      </div>
    </div>
  );
}

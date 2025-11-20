import React, {useState} from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Download, X } from "lucide-react";

export default function ExportModal({ isOpen, onClose, html, style }) {
    const [fileName, setFileName] = useState("");
    const [fileType, setFileType] = useState("");
    const newHtml = `<html><head><style>${style}</style></head><body>${html}</body></html>`
const handleExport = async () => {
  if (!fileType || !fileName) {
    alert("Please enter file name and select file type");
    return;
  }

  try {
    if (fileType.toLowerCase() === "pdf") {
      const res = await fetch("http://localhost:4000/api/export/pdf", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          html: newHtml,
          filename: fileName, // match backend key
        }),
      });

      if (!res.ok) throw new Error(`Export failed (${res.status})`);

      // If the backend returns a PDF file
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${fileName}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);

      console.log("Export successful");
      onClose();
    }
  } catch (err) {
    console.error("Error exporting:", err);
  }
};


  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="bg-white/10 border border-white/20 shadow-2xl rounded-2xl p-8 w-[400px] backdrop-blur-md text-white"
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
          >
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold tracking-wide">Export File</h2>
              <button
                onClick={onClose}
                className="text-gray-300 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Body */}
            <div className="space-y-5">
              <div>
                <label className="block text-sm mb-2 text-gray-300">
                  File Name
                </label>
                <input
                  id="input"
                  placeholder="Enter file name..."
                  className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => setFileName(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm mb-2 text-gray-300">
                  File Type
                </label>
                <select
                  id="select"
                  className="w-full text-shadow-black px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => setFileType(e.target.value)}
                >
                  <option value="">-- Select file type --</option>
                  <option className="text-shadow-black">PDF</option>
                </select>
              </div>
            </div>

            {/* Footer */}
            <div className="flex justify-end mt-8">
              <button
                onClick={handleExport}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-5 py-2 rounded-lg font-medium transition-colors"
              >
                <Download size={18} />
                Export
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

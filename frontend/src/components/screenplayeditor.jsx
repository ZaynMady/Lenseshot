import React, { useEffect, useState, useRef, forwardRef, useImperativeHandle } from "react";

const ScreenplayEditor = forwardRef(({ screenplayJson, ActiveComponent, setActiveComponent }, ref) => {
  const [lines, setLines] = useState([]);
  const [activeLine, setActiveLine] = useState(0);
  const linesRef = useRef([]);
  const editorRef = useRef(null);

  // ✅ Expose a getter for parent
  useImperativeHandle(ref, () => ({
    getScreenplayData: () => {
      return linesRef.current.map((line) => ({
        class: line.class,
        content: line.content,
      }));
    },
  }));

  // ✅ Initialize screenplay lines
  useEffect(() => {
    const initial = screenplayJson?.length
      ? screenplayJson
      : [{ class: "scene-heading", content: "" }];

    setLines(initial);
    linesRef.current = initial;
  }, [screenplayJson]);

  const focusLine = (index, placeAtEnd = true) => {
    const editor = editorRef.current;
    const lineDiv = editor?.children[index];
    if (!lineDiv) return;

    lineDiv.focus();
    const sel = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(lineDiv);
    if (placeAtEnd) range.collapse(false);
    sel.removeAllRanges();
    sel.addRange(range);
  };

  useEffect(() => {
    const editor = editorRef.current;
    const lineEl = editor?.children?.[activeLine];
    const lineData = linesRef.current[activeLine];

    if (lineEl && lineData) {
      lineData.class = ActiveComponent;
      lineEl.className = `${ActiveComponent} bg-yellow-50`;
      requestAnimationFrame(() => focusLine(activeLine, false));
    }
  }, [ActiveComponent]);

  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) return;
    const linesEls = Array.from(editor.children);
    linesEls.forEach((el, i) => el.classList.toggle("bg-yellow-50", i === activeLine));
    requestAnimationFrame(() => focusLine(activeLine, false));

    const current = linesRef.current[activeLine];
    if (current) setActiveComponent(current.class);
  }, [activeLine]);

  const handleInput = (e, index) => {
    linesRef.current[index].content = e.target.textContent;
  };

  const handleKeyDown = (e, index) => {
    const currentLine = linesRef.current[index];
    const currentText = currentLine.content;
    setActiveComponent(currentLine.class);

    if (e.key === "Enter") {
      e.preventDefault();
      let newClass = "action";
      if (currentLine.class === "character") newClass = "dialogue";
      if (currentLine.class === "scene-heading") newClass = "action";
      if (currentLine.class === "dialogue") newClass = "action";

      const newLines = [
        ...linesRef.current.slice(0, index + 1),
        { class: newClass, content: "" },
        ...linesRef.current.slice(index + 1),
      ];
      linesRef.current = newLines;
      setLines(newLines);
      setActiveLine(index + 1);
    }

    if (e.key === "Backspace" && currentText === "" && linesRef.current.length > 1) {
      e.preventDefault();
      const newLines = [...linesRef.current];
      newLines.splice(index, 1);
      linesRef.current = newLines;
      setLines(newLines);
      setActiveLine(Math.max(0, index - 1));
    }

    if (e.key === "Tab") {
      e.preventDefault();
      const order = ["action", "character", "dialogue"];
      const currentIdx = order.indexOf(currentLine.class);
      const nextClass = order[(currentIdx + 1) % order.length];
      linesRef.current[index].class = nextClass;
      currentLine.class = nextClass;
      setLines([...linesRef.current]);
      setActiveComponent(nextClass);
    }
  };

  return (
    <div ref={editorRef} className="mx-auto mt-4 p-4 outline-none">
      {lines.map((line, index) => (
        <div
          key={index}
          className={`${line.class} ${activeLine === index ? "bg-yellow-50" : ""}`}
          contentEditable
          suppressContentEditableWarning
          onInput={(e) => handleInput(e, index)}
          onKeyDown={(e) => handleKeyDown(e, index)}
          onClick={() => setActiveLine(index)}
          spellCheck={false}
        >
          {line.content}
        </div>
      ))}
    </div>
  );
});

export default ScreenplayEditor;

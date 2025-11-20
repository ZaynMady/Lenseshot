import React, {
  useEffect,
  useState,
  useRef,
  forwardRef,
  useImperativeHandle,
} from "react";

const PAGE_HEIGHT = 700; // A4 height in px

const ScreenplayEditor = forwardRef(
  ({ screenplayJson, ActiveComponent, setActiveComponent, styles, componentRef }, ref) => {
    const [lines, setLines] = useState([]);
    const [activeLine, setActiveLine] = useState(0);
    const [breakIndexes, setBreakIndexes] = useState([]);
    const linesRef = useRef([]);
    const editorRef = useRef(null);
    const containerRef = useRef(null);


    // Expose screenplay data externally
    useImperativeHandle(ref, () => ({
      getScreenplayData: () =>
        linesRef.current.map((line) => ({
          class: line.class,
          content: line.content,
        })),
      getScreenplayHtml: () => containerRef.current?.innerHTML,
    }));

    //making line class and active component interdependent
// ✅ Only update line class if user changes ActiveComponent while staying on same line
      useEffect(() => {
        const currentLine = linesRef.current[activeLine];
        if (!currentLine) return;

        // If user selected a new component, apply it to the current line
        if (currentLine.class !== ActiveComponent) {
          currentLine.class = ActiveComponent;
          setLines([...linesRef.current]);
        }
      }, [ActiveComponent]);


    // Initialize lines
    useEffect(() => {
      let initial;
      if (screenplayJson?.length) {
        initial = screenplayJson;
      } else {
        setActiveComponent("scene-heading");
        initial = [{ class: "scene-heading", content: "" }];
      }
      setLines(initial);
      linesRef.current = initial;
    }, [screenplayJson, setActiveComponent]);

    const focusLine = (index, placeAtEnd = true) => {
      const editor = editorRef.current;
      const lineDiv = editor?.querySelector(`[data-line="${index}"]`);
      if (!lineDiv) return;
      const sel = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(lineDiv);
      if (placeAtEnd) range.collapse(false);
      sel.removeAllRanges();
      sel.addRange(range);
      lineDiv.focus();
    };

    // Highlight current line and set active component
    useEffect(() => {
      const editor = editorRef.current;
      if (!editor) return;

      const allLines = editor.querySelectorAll("[data-line]");
      allLines.forEach((el, i) =>
        el.classList.toggle("bg-yellow-50", i === activeLine)
      );

      const activeLineEl = editor.querySelector(`[data-line="${activeLine}"]`);
      if (activeLineEl) {
        // Automatically scroll the active line to the center of the view
        activeLineEl.scrollIntoView({ block: "center", behavior: "smooth" });
      }

      requestAnimationFrame(() => focusLine(activeLine, false));

      const current = linesRef.current[activeLine];
      if (current) {
        // ✅ Active line always sets activeComponent (unless user overrides later)
        setActiveComponent(current.class);
      }
    }, [activeLine]);


    // Track text changes
    const handleInput = (e, index) => {
      linesRef.current[index].content = e.target.textContent;
    };

    // Keyboard logic
    const handleKeyDown = (e, index) => {
      const currentLine = linesRef.current[index];
      const currentText = currentLine.content;

      if (e.key === "Enter") {
        e.preventDefault();
        let nextClass = "action"; // Default
        switch (currentLine.class) {
          case "scene-heading":
          case "action":
          case "setting":
            nextClass = "action";
            break;
          case "character":
            nextClass = "dialogue";
            break;
          case "dialogue":
            nextClass = "action";
            break;
        }
        const newLines = [
          ...linesRef.current.slice(0, index + 1),
          { class: nextClass, content: "" },
          ...linesRef.current.slice(index + 1),
        ];
        linesRef.current = newLines;
        setLines(newLines);
        setActiveLine(index + 1);
        setActiveComponent(nextClass);
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
        const order = ["action", "character", "dialogue", "transition", "shot", "scene-heading"];
        const currentIdx = order.indexOf(currentLine.class);
        const nextClass = order[(currentIdx + 1) % order.length];
        linesRef.current[index].class = nextClass;
        currentLine.class = nextClass;
        setLines([...linesRef.current]);
        setActiveComponent(nextClass);
      }
    };

    // ✅ Detect overflow and calculate where to place visual page breaks
    useEffect(() => {
      const editor = editorRef.current;
      if (!editor) return;

      const children = Array.from(editor.querySelectorAll("[data-line]"));
      let height = 0;
      const newBreakIndexes = [];

      children.forEach((child, i) => {
        const lineHeight = child.offsetHeight || 0;
        height += lineHeight;

        // When overflow occurs, mark this line index for a page break
        if (height > PAGE_HEIGHT) {
          newBreakIndexes.push(i);
          height = lineHeight;
        }
      });

      // ✅ Only update if the breaks actually changed
      const changed =
        newBreakIndexes.length !== breakIndexes.length ||
        newBreakIndexes.some((v, i) => v !== breakIndexes[i]);

      if (changed) setBreakIndexes(newBreakIndexes);
    }, [lines]);

    return (
      <>
        <style>{styles}</style>
        <div ref={containerRef}>
        <div
          ref={editorRef}
          className="page"
          style={{
            background: "white",
            width: "794px",
            minHeight: "1200px",
            margin: "40px auto",
            padding: "40px",
            boxShadow: "0 0 10px rgba(0,0,0,0.1)"
          }}
        >

          {lines.map((line, index) => (
            <React.Fragment key={index}>
              <div
                data-line={index}
                className={`${line.class} ${
                  activeLine === index ? "bg-yellow-50" : ""
                }`}
                contentEditable
                suppressContentEditableWarning
                onInput={(e) => handleInput(e, index)}
                onKeyDown={(e) => handleKeyDown(e, index)}
                onClick={() => setActiveLine(index)}
                spellCheck={false}
                style={{
                  position: "relative",
                  zIndex: 1,
                  paddingBottom: "2px",
                }}
              >
                {line.content}
              </div>

              {/* ✅ Visual non-editable page breaks */}
              {breakIndexes.includes(index + 1) && (
                <div
                  className="page-break border-t-2 border-dashed border-gray-300 my-6 text-center text-gray-400 text-xs select-none pointer-events-none"
                  key={`break-${index}`}
                >
                  Page {breakIndexes.indexOf(index + 1) + 2}
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
        
        </div>
        </>
    );
  }
);

export default ScreenplayEditor;

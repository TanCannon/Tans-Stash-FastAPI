// import { validateAsciiTree } from "./asciiToZipEditorEngine.js";
import { validateUnicodeTree, createErrorState, applyErrors} from "./asciiToZipEditorEngine.js";

function unicodeToAscii(text) {
  return text.replace(/├─/g, "|--").replace(/└─/g, "`--").replace(/│/g, "|");
}

function asciiToUnicode(text) {
  return text
    .replace(/(\|--)/g, "├─")
    .replace(/`--/g, "└─")
    .replace(/\|/g, "│");
}

function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

//wrapping inside window event to wait for js for CodeMirror to load.
window.addEventListener("DOMContentLoaded", () => {
  // Create editors
  const unicodeBox = CodeMirror(document.getElementById("unicodeEditor"), {
    lineNumbers: true,
    lineWrapping: true,
    mode: "text/plain",
    theme: "material",
    gutters: ["CodeMirror-linenumbers", "unicode-tree-errors"],
    value: "",
    placeholder: "Paste a UNICODE tree here (│ ├ └)\n\nExample:\nproject/\n├─ src/\n│  └─ main.py\n└─ README.md",
  });

  const asciiBox = CodeMirror(document.getElementById("asciiEditor"), {
    lineNumbers: true,
    lineWrapping: true,
    mode: "text/plain",
    theme: "material",
    gutters: ["CodeMirror-linenumbers", "ascii-tree-errors"],
    value: "",
    placeholder: "This is the ASCII tree view\n\nEdit your tree here with ASCII symbols on keyboard they mirror automatically on the left side:\nproject/\n|-- src/\n|   `-- main.py\n`-- README.md",
  });

  //error states to manage old and new errors.
  const unicodeErrorState = createErrorState();
  const asciiErrorState = createErrorState();

  // Mirror cursor between editors
  function mirrorCursor(source, target) {
    const cursor = source.getCursor();
    target.setCursor(cursor);
  }

  //sync error to ascii code editor
  // /*
  const syncErrorsToAscii = debounce(() => {
    const errors = validateUnicodeTree(unicodeBox);

    applyErrors({
      cm: asciiBox,
      lines: asciiBox.getValue().split("\n"),
      errors,
      state: asciiErrorState,
      gutterName: "ascii-tree-errors"
    });
  }, 0);
  // */

  const handleUnicode = debounce((instance, changeObj) => {
    // Ignore internal updates caused by setValue
    if (changeObj.origin === "setValue") return;

    const text = unicodeBox.getValue();
    asciiBox.setValue(unicodeToAscii(text));
    // /*
    syncErrorsToAscii();
    // */
    mirrorCursor(unicodeBox, asciiBox);
  }, 300);

  const handleAscii = debounce((instance, changeObj) => {
    // Ignore internal updates caused by setValue
    if (changeObj.origin === "setValue") return;

    const text = asciiBox.getValue();
    unicodeBox.setValue(asciiToUnicode(text));
    syncErrorsToAscii();
    mirrorCursor(asciiBox, unicodeBox);
  }, 300);

//   unicodeBox.on("change", handleUnicode);
  function onUnicodeChange(unicodeEditor, asciiEditor, changeObj) {
    handleUnicode(unicodeEditor, changeObj);

    const errors = validateUnicodeTree(unicodeEditor);

    applyErrors({
      cm: unicodeEditor,
      lines: unicodeEditor.getValue().split("\n"),
      errors,
      state: unicodeErrorState,
      gutterName: "unicode-tree-errors"

    });
  }
  unicodeBox.on("change", (cm, changeObj) => {
    // console.log("asciiBox:", asciiBox);
    onUnicodeChange(cm, asciiBox, changeObj);
  });

  asciiBox.on("change", (cm, changeObj) => {
    handleAscii(cm, changeObj);
  });

  // asciiBox.on("change", handleAscii);

  // Highlight on focus
  unicodeBox.on("focus", () => {
    unicodeBox.getWrapperElement().classList.add("cm-editor-active");
    asciiBox.getWrapperElement().classList.remove("cm-editor-active");
  });

  asciiBox.on("focus", () => {
    asciiBox.getWrapperElement().classList.add("cm-editor-active");
    unicodeBox.getWrapperElement().classList.remove("cm-editor-active");
  });

  // Remove highlight if both lose focus (optional)
  [unicodeBox, asciiBox].forEach((editor) => {
    editor.on("blur", () => {
      setTimeout(() => {
        if (!document.activeElement.closest(".CodeMirror")) {
          editor.getWrapperElement().classList.remove("cm-editor-active");
        }
      }, 100);
    });
  });

  // Copy buttons
  async function copyToClipboard(target) {
    const text =
      target === "unicodeEditor" ? unicodeBox.getValue() : asciiBox.getValue();

    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error("Failed to copy:", err);
      alert("Failed to copy");
    }
  }

  //copy buttons
  document.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-target");
      copyToClipboard(target);
      btn.textContent = "Copied!";
      setTimeout(() => (btn.textContent = "Copy"), 1200);
    });
  });

  //geneate zip button and //form validation for editor to check for empty submission
  document.getElementById("treeForm").addEventListener("submit", function (e) {
    /* ---- 1. if editor is empty ---- */
    const unicodetext = unicodeBox.getValue();
    if (unicodetext.trim()) {
      document.getElementById("unicodeHidden").value = unicodetext;
    } else {
      e.preventDefault(); // stop form submission
      alert("Please input a valid tree into the editor.");
    }

    /* --- 2. if some errors exists in the editor --- */
    if (unicodeErrorState.textMarkers.length > 0){
      if (!confirm("There are some errrors in the tree, the results may not satisfy you. You still want to proceed?")){
        e.preventDefault(); // stop form submission
      }
    }
  });
});

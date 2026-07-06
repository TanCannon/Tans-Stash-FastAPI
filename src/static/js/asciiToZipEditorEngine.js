const LINE_REGEX = /^(?:([A-Za-z0-9._-]+\/?)|((?:│ {2}| {2})*)(├─|└─) ([A-Za-z0-9._-]+\/?))$/;

// const LINE_REGEX =
// /^(?: 
//   ([A-Za-z0-9._-]+\/?)                      // (1) ROOT line: project/
//   |                                         // OR
//   ((?:│ {2}| {3})*)                         // (2) INDENT blocks
//   (├─|└─)                                   // (3) BRANCH
//   ([A-Za-z0-9._-]+\/?)                      // (4) NAME
// )$/;

function createGutterError(message) {
    const marker = document.createElement("div");
    marker.className = "ascii-tree-error-marker";
    marker.innerHTML = "●"; // simple red dot
    marker.title = message; // tooltip
    return marker;
}

function clearErrors(cm, state, gutterName) {
  state.textMarkers.forEach(m => m.clear());
  state.textMarkers.length = 0;

  state.gutterMarkers.forEach(({ line }) => {
    cm.setGutterMarker(line, gutterName, null);
  });
  state.gutterMarkers.length = 0;
}

export function createErrorState() {
  return {
    textMarkers: [],
    gutterMarkers: []
  };
}

export function applyErrors({
  cm,
  lines,
  errors,
  state,
  gutterName,
  className = "cm-error-line"
}) {
  clearErrors(cm, state, gutterName);

  errors.forEach(err => {
    const lineIndex = err.line - 1;

    if (lineIndex < 0 || lineIndex >= lines.length) return;

    // Highlight line
    const marker = cm.markText(
      { line: lineIndex, ch: 0 },
      { line: lineIndex, ch: lines[lineIndex].length },
      {
        className,
        title: err.message
      }
    );

    state.textMarkers.push(marker);

    // Gutter marker
    const gutterMarker = createGutterError(err.message);
    cm.setGutterMarker(lineIndex, gutterName, gutterMarker);

    state.gutterMarkers.push({ line: lineIndex });
  });
}

function error(line, message) {
    return { line, message };
}

function explainSpaceMismatch(line) {
  // 1. Tabs
  if (/\t/.test(line)) {
    return "Tabs detected. Use spaces only.";
  }

  // 2.1 Leading spaces before content (invalid indent units)
  if (/^( +)/.test(line)) {
    const leading = line.match(/^( +)/)[1];

    // Strip valid indent units: "│  " or "  "
    const remainder = leading.replace(/(│ {2}| {2})/g, "");

    if (remainder.length > 0) {
      return "Invalid leading spaces. Please remove leading spaces.";
    }
  }

  // 2.2 Trailing spaces
  if (/[ \t]+$/.test(line)) {
    return "Trailing spaces at the end of the line are not allowed.";
  }

  // 3. More than one space after branch
  if (/(├─|└─)\s{2,}/.test(line)) {
    return "Too many spaces after branch symbol. Use exactly one space.";
  }

  // 4. No space after branch
  if (/(├─|└─)[^\s]/.test(line)) {
    return "Missing space after branch symbol.";
  }

  // 5. Broken indentation groups
  const indentMatch = line.match(/^([│ ]+)/);
  if (indentMatch) {
    const indent = indentMatch[1];

    // Remove all valid indent chunks
    const remainder = indent.replace(/(│ {2}| {2})/g, "");

    if (remainder.length > 0) {
      return (
        "Invalid indentation spacing. Keep 2 spaces between indents e.g:\n" +
        "• '│␠␠|' or\n" +
        "• '│␠␠├─'"
      );
    }
  }

  return null; // spacing is consistent
}

function explainSymbolMismatch(line) {
  // ASCII branch symbols
  if (/\|--|\+--|`--/.test(line)) {
    return "ASCII branch symbols detected. Use Unicode branches: '├─' or '└─'.";
  }

  // Wrong Unicode dash count
  if (/├──|└──/.test(line)) {
    return "Invalid branch length. Use exactly one dash: '├─' or '└─'.";
  }

  // Missing space after branch
  if (/(├─|└─)[^\s]/.test(line)) {
    return "Missing space after branch symbol. Use '├─ name' or '└─ name'.";
  }

  // Vertical pipe without branch
  if (/│/.test(line) && !/(├─|└─)/.test(line)) {
    return "Dangling vertical pipe '│' without a branch symbol.";
  }

  // Mixed ASCII and Unicode symbols
  if (/(│|├─|└─)/.test(line) && /[|+`]/.test(line)) {
    return "Mixed ASCII and Unicode tree symbols detected. Use Unicode only.";
  }

  return null; // symbols are consistent
}

function explainLineError(line){
  let msg = explainSymbolMismatch(line);
  if ( msg != null){
    return msg;
  }

  msg = explainSpaceMismatch(line);
  
  if ( msg != null){
    return msg;
  }

  msg = "Invalid File Name. Don't use more than one / or spaces in names."

  return msg;
}

function tokenizeLine(line, lineNumber) {
    const match = line.match(LINE_REGEX);

    if (!match) {
        // throw error(lineNumber, "Invalid line format");
        throw error(lineNumber, explainLineError(line));
    }

    let indent = 0;
    let branch = null;
    let name = null;

    // Case 1: root line
    if (match[1]) {
        name = match[1];
        indent = -1;
    }
    // Case 2: indented tree line
    else {
        const indentRaw = match[2];
        branch = match[3];
        name = match[4];

        // Each indent level is exactly one block: "│  " or "   "
        indent = indentRaw.length / 3;
    }

    if (!name) {
        throw error(lineNumber, "Missing file or folder name");
    }

    return {
        indent,
        branch,               // null for root
        name,
        isFolder: name.endsWith("/"),
        line: lineNumber
    };
}

// --- kind of a forest builder but just using two states as current line depends on the property of its previous line.
function parseAsciiTree(text) {
    const errors = [];
    let prevLine = null;

    //sanitize and extract line into a array lines.
    const lines = text
    .replace(/\t/g, "   ")
    .split("\n")
    .map(l => l.trimEnd())          // remove trailing spaces only
    .filter(l => l.trim().length > 0);

    function addError(line, message){
      /* --- currently showing one error at a time --- */
      if (errors.length == 0){
        errors.push({ line, message });
      }
      else{
        return;
      }
    }

    lines.forEach((line, index) => {
        const lineNumber = index + 1;
        //console.log(`Line: ${line}, LineNo: ${lineNumber}`);

        let token;
        try {
            //token = {indent, branch, name, isFolder, line}
            token = tokenizeLine(line, lineNumber);
            //console.log(`Token: Indent- ${token.indent}, Branch- ${token.branch}, Name- ${token.name}, isFolder- ${token.isFolder}, LineNo- ${token.lineNumber}`);
        } catch (e) {
            // addError(e.line, e.message);
            addError(e.line, e.message);
            return; // skip this line, continue
        }

        //
        if (prevLine != null){
            //INDENTATION is not valid
            let allowedIndent = prevLine.indent;
            //for a child inside a folder
            if (prevLine.isFolder){
                allowedIndent = prevLine.indent + 1;
            }

            if (token.indent > allowedIndent){
                addError(token.line, `Invalid indentation(current ${token.indent}, expected ≤ ${allowedIndent})`);
                return;
            }
            //if INDENTATION is correct but if BRANCH ended
            else{
                if (prevLine.indent == token.indent && prevLine.branch == "└─" && !prevLine.isFolder){
                    addError(token.line, `Invalid tree syntax, this branch is ended above by └─ please remove └─ to add more on this branch`);
                    return;
                }
                //console.log("Branch error");
            }
        }
        else{
            // ROOT NODE validation
            if (!token.isFolder){
                addError(token.line, `Child defined before any root`)
                return;
            }
        }

        prevLine = token;
    });

    errors.forEach(err => {
        //console.log(`errors: ${err.line, err.message}`);
    })
    
    return errors;

}

export function validateUnicodeTree(cm) {
    const text = cm.getValue();
    const lines = text.split("\n");

    //console.log("runi");
    const errors = parseAsciiTree(text);

    return errors;
}

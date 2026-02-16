import os, re, zipfile

def create_structure_from_ascii(ascii_structure: str, base_dir: str):
    lines = ascii_structure.strip().splitlines()
    stack = [(0, base_dir)]  # Each item: (indent, full_path)
    for line in lines:
            if not line.strip():
                continue

            # Extract name after ├─, └─, or take root but leave '/' at the end
            match = re.search(r"[├└]─\s*(.*)", line)
            if match:
                name = match.group(1).strip()
            else:
                name = line.strip()
            # print(f"name: {name}")

            # Compute indentation: number of leading spaces before the name
            leading = line[:line.find(name)] if name in line else ""
            # print(f"leading: {leading}")
            indent = len(leading.replace("│", " "))  # treat pipes as spaces

            # Find the parent in the stack with indentation < current indent
            parent_path = None
            for i in range(len(stack)-1, -1, -1):
                if stack[i][0] < indent:
                    parent_path = stack[i][1]
                    break
            if parent_path is None:
                # No parent found → root-level folder
                parent_path = base_dir

            # Full path
            full_path = os.path.join(parent_path, name.rstrip("/"))

            # print(full_path)  # print instead of creating

            # '''create the directory'''
            

            # If directory, push to stack
            if name.endswith("/"):
                # It's a directory → create it if not exists
                os.makedirs(full_path, exist_ok=True)
                stack.append((indent, full_path))
            
            else:
                # It's a file → create an empty file
                os.makedirs(os.path.dirname(full_path), exist_ok=True)  # make sure parent exists
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write("")  # empty placeholder file

def printSomething():
    print("Happy New Year 2026  ")

def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            # Add empty directories
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                arcname = os.path.relpath(dir_path, folder_path) + "/"  # force trailing /
                zipf.writestr(arcname, "")  # add empty entry for folder

            # Add files
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)  # relative path in zip
                zipf.write(file_path, arcname)

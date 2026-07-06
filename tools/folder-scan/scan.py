import os

parent_folder = r"REPLACE\WITH\PATH"
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, "OTCBSPECR.txt")

with open(output_file, "w", encoding="utf-8") as f:

    for root, dirs, files in os.walk(parent_folder):
        dirs.sort()
        files.sort()

        # Skip writing a line for the parent folder itself
        if root == parent_folder:
            depth = 0
        else:
            rel_path = os.path.relpath(root, parent_folder)
            depth = rel_path.count(os.sep) + 1
            indent = "    " * (depth - 1)
            folder_name = os.path.basename(root)
            f.write(f"{indent}{folder_name}\n")

        file_indent = "    " * depth
        for file in files:
            f.write(f"{file_indent}{file}\n")

        if files or dirs:
            f.write("\n")

print(f"File list saved to: {output_file}")
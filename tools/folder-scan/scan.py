import os

parent_folder = r"E:\6 GAMES\1. Playstation 1\Option.Tuning.Car.Battle.2.JAP.PS1-ZTM\Extracted"

script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, "folder_file_list.txt")

with open(output_file, "w", encoding="utf-8") as f:
    
    for folder_name in sorted(os.listdir(parent_folder)):
        folder_path = os.path.join(parent_folder, folder_name)
        
        if os.path.isdir(folder_path):
            f.write(f"{folder_name}\n")
            
            files = sorted(os.listdir(folder_path))
            
            for file in files:
                file_path = os.path.join(folder_path, file)
                
                if os.path.isfile(file_path):
                    f.write(f"    {file}\n")
            
            f.write("\n") 

print(f"File list saved to: {output_file}")
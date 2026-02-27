import struct
import numpy as np

def load_car_file(file_path):
    mesh_entries = parse_car_file(file_path)
    meshes = parse_mesh_data(file_path, mesh_entries)
    return meshes

def parse_car_file(file_path):
    with open(file_path, 'rb') as file:
        file.seek(0)
        mesh_count, table_offset = struct.unpack('<II', file.read(8))
        print(f"Mesh count: {mesh_count}, Table offset: {table_offset}")
        
        file.seek(table_offset)
        mesh_entries = []
        for _ in range(mesh_count):
            offset, count = struct.unpack('<II', file.read(8))
            mesh_entries.append((offset, count))
            print(f"Mesh entry - Offset: {offset}, Count: {count}")
        
        return mesh_entries

def parse_mesh_data(file_path, mesh_entries):
    meshes = []
    with open(file_path, 'rb') as file:
        for offset, count in mesh_entries:
            file.seek(offset)
            vertices = []
            indices = []
            
            print(f"\nParsing mesh at offset {offset}, with {count} vertices")
            remaining_data = file.read()
            print(f"Remaining data: {len(remaining_data)} bytes")

            # Read vertex data (check if we have enough data)
            for i in range(count):
                vertex_data = file.read(6)  # 3x 16-bit signed integers (for x, y, z)
                if len(vertex_data) != 6:
                    print(f"Error reading vertex {i}: not enough data left in file!")
                    break
                x, y, z = struct.unpack('<hhh', vertex_data)
                vertices.append((x, y, z))

            # Read the triangle data (indices)
            triangles_read = 0
            for _ in range(count // 3):  # Assuming each mesh has triangles
                triangle_data = file.read(12)  # 3x 32-bit indices
                if len(triangle_data) != 12:
                    print(f"Error reading triangle data: not enough data left!")
                    break
                i1, i2, i3 = struct.unpack('<III', triangle_data)
                indices.append((i1, i2, i3))
                triangles_read += 1
            
            meshes.append((np.array(vertices), np.array(indices)))
    
    return meshes
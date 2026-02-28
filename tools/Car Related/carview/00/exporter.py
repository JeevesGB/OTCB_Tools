def export_obj(path, vertices, faces, scale=1.0):
    with open(path, "w") as f:
        for v in vertices:
            f.write(f"v {v.x*scale} {v.y*scale} {v.z*scale}\n")

        for face in faces:
            idxs = [i+1 for i in face.indices]
            f.write("f " + " ".join(map(str, idxs)) + "\n")
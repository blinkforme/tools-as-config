import os
import sys

path = "/Users/peterpuppy/code/Arthas/Arthas/Assets/Src/Lua/Fight"

walk_path = path
paths = []
for (dirpath, dirnames, filenames) in os.walk(walk_path):
    for f in filenames:
        # print(dirnames)
        if not f.endswith("meta"):
            parent = dirpath.replace("/Users/peterpuppy/code/Arthas/Arthas/Assets/Src/Lua/", "").replace("/",".")
            fileName = f.split(".")[0]
            # print(parent + "." + fileName)
            print("require\"{name}\"".format(name=parent + "." + fileName))
        #
        # print("require\"Proto.{fileName}\"".format(fileName = fileName))
        # if not f.startswith('~') and not f.startswith('.'):
        #     paths.append(os.path.join(walk_path, f))

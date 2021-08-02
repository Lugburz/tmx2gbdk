import os
import time
import tmx2gbdk

# this module loops over a folder and subfolders every n seconds
# so it can call tmx2gbdk regularly

def deep_get_tmx(directory, concat):
    for file in os.listdir(directory):
        j = os.path.join(directory, file)
        if file.endswith(".tmx"):
            concat.append(j)
        if os.path.isdir(j):
            deep_get_tmx(j, concat)
    return concat

root = '.'
verbose = True


while(1):
    all_files = deep_get_tmx(root, [])

    print(all_files)

    for file in all_files:
        tmx2gbdk.convert_tmx(file, verbose)
    time.sleep(5)
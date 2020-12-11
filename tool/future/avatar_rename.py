# -*- coding: utf-8 -*-

import json
import os
import urllib

folder_path = "avatars"

count = 0
for (dirpath, dirnames, filenames) in os.walk(folder_path):
    for f in filenames:
        new_file_name = str(count) + '.png'

        src_path = os.path.abspath(os.path.join(dirpath, f))
        target_path = os.path.abspath(os.path.join(dirpath, new_file_name))

        print "rename", src_path, target_path

        os.rename(src_path, target_path)

        count = count + 1

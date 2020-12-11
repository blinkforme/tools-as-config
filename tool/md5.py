# -*- coding: utf-8 -*-
import hashlib
import json
import os
import shutil
import sys
import time

from assassin import write_file
from md5_config import pmap

FILE_PATHS = []

project_index = 0

ABS_PATH = ""
TARGET_PATH = ""
MANIFEST_PATH = ""
COPY_FILES = {}
INDEX_HTMl_PATH = ""
MAIN_JS_PATH = ""


def md5(path):
    with open(path, 'rb') as inputfile:
        data = inputfile.read()

        md5_digest = hashlib.md5(data).hexdigest()
        return md5_digest


def init():
    global ABS_PATH
    global TARGET_PATH
    global MANIFEST_PATH
    global COPY_FILES
    global INDEX_HTMl_PATH
    global MAIN_JS_PATH

    CONFIG = pmap[project_index]
    PREFIX = CONFIG.get('PREFIX', "")

    ABS_PATH = os.path.join(PREFIX, CONFIG['ABS_PATH'])
    TARGET_PATH = os.path.join(PREFIX, CONFIG['TARGET_PATH'])
    MANIFEST_PATH = os.path.join(PREFIX, CONFIG['MANIFEST_PATH'])

    TEMP_COPY_FILES = CONFIG['COPY_FILES']

    for key in TEMP_COPY_FILES:
        COPY_FILES[os.path.join(PREFIX, key)] = os.path.join(PREFIX, TEMP_COPY_FILES[key])

    if CONFIG.get("INDEX_HTMl_PATH", ""):

        INDEX_HTMl_PATH = os.path.join(PREFIX, CONFIG['INDEX_HTMl_PATH'])
    else:
        INDEX_HTMl_PATH = ""
    MAIN_JS_PATH = os.path.join(PREFIX, CONFIG['MAIN_JS_PATH'])

    # 清空目标文件夹
    if os.path.exists(TARGET_PATH):
        shutil.rmtree(TARGET_PATH)

    #
    shutil.copytree(ABS_PATH, TARGET_PATH)

    for key in COPY_FILES:
        dirpath = os.path.dirname(os.path.realpath(COPY_FILES[key]))
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        shutil.copyfile(key, COPY_FILES[key])

    if INDEX_HTMl_PATH and MAIN_JS_PATH:
        MAIN_JS_MD5 = md5(MAIN_JS_PATH)
        replace(INDEX_HTMl_PATH, 'Main.max', MAIN_JS_MD5)


def replace(path, word, word_replace):
    print('replace')
    print(path)
    # Read in the file
    with open(path, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(word, word_replace)

    # Write the file out again
    with open(path, 'w') as file:
        file.write(filedata)


def get_pngs(folder_path):
    """
    遍历文件夹，找出所有的PNG的绝对路径
    :param folder_path:文件夹路径
    :return:路径数组
    """
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        for f in filenames:
            if not f.endswith(".mp3") and not f.endswith(".ttf"):
                file_path = os.path.join(dirpath, f)
                FILE_PATHS.append(file_path)


def main():
    init()

    get_pngs(TARGET_PATH)
    dic = {}

    for path in FILE_PATHS:

        if path.endswith('html'):
            continue

        md5_digest = md5(path)

        parent_path, filename = os.path.split(path)

        f_name, suffix = os.path.splitext(filename)
        new_file_name = md5_digest + suffix
        new_file_name_path = os.path.join(parent_path, new_file_name)

        if not os.path.exists(new_file_name_path):
            os.rename(path, new_file_name_path)

        relpath = os.path.relpath(path, TARGET_PATH)
        md5_relpath = os.path.relpath(new_file_name_path, TARGET_PATH)

        dic[relpath.replace('\\', '/')] = md5_relpath.replace('\\', '/')

    write_file(json.dumps(dic), os.path.join(MANIFEST_PATH, 'manifest_{ts}.json'.format(ts=str(int(time.time())))))
    if INDEX_HTMl_PATH:
        replace(INDEX_HTMl_PATH, '{{MANIFEST}}', json.dumps(dic))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        index = int(sys.argv[1])
        project_index = index

    main()

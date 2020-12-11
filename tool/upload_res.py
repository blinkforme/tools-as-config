# -*- coding: utf-8 -*-
from qiniu import Auth, put_file, etag, BucketManager
import argparse
import os
import hashlib
import tinify
import json
import time
import random
# 七牛
QINIU_ACCESSKEY = 'b67u1ysMlZLUzT43FRArPP7I6xOuwQbWUJOAm-ed'
QINIU_SECRETKEY = 'RBAWG1VQGeSn_OON6SUmE18E49n7WoaxlDyedVJ7'
QINIU_BUCKET = 'h5sq'
QINIU_DOMAIN = 'https://sq-img.jjhgame.com'

uq = Auth(QINIU_ACCESSKEY, QINIU_SECRETKEY)

bucket = BucketManager(q)
cache = {}

API_KEYS = [
    "FX9lrsc1h9ct8eH3LeeH3sFhDw68PtsV",
    "2pejTbKzD7VhxgrWcbRjiMeTb0eEZkbx",
    "2XlrTo2oRLdhPaRxo71J8UPeJ5fcRTWe",
    "7GmWlZOZJ0mjBVPWX9ExElNqz0XYQDq8",
    "6XQFKpolEJQKw7Qx7elpchvEcVudvYfn",
    "qKEbo0Iwod0zHaS43sR4TM4ByQJWOYTB",
    "nsJOH9uvowE2KAZXK4Ir02D1zFXl89C8",
    "rcnvWw7clC2RbqbzrL3i38OUXbfNn8lY",
    "UTfpG9C3nuP70wzz0UWyxzgVUEdGbDFn",
    "PhXZtfxrybxMDUxj33j7BchRepfnEWlI",
    "ZmhfvnkC0Y4AlPHzfFKPB3B3gllRnyWw",
    "DrI0ILRARz8cD4kazHw1ZwZEdt2wDvFL",
]

random.randint(0, len(API_KEYS)-1)
tinify.key = API_KEYS[0]


def compress_png(path):
    """
    压缩一张图片
    :param path:
    :return:
    """

    before_size = os.path.getsize(path)
    try:
        source = tinify.from_file(path)
        source.to_file(path)
    except tinify.AccountError as  e:
        print(e)
        print("发生AccountError ,请切换账号")
        # next_key()

    except Exception as e:
        print(e)
        print("压缩失败,第一次：" + path)

        try:
            source = tinify.from_file(path)
            source.to_file(path)
        except Exception as  e:
            print(e)

    after_size = os.path.getsize(path)
    print("压缩成功({path})，压缩{before_size}KB =>{after_size}KB,压缩 {reduce}%".format(
        before_size=before_size / 1000,
        after_size=after_size / 1000, path=path,
        reduce=round(float(before_size - after_size) / before_size, 2) * 100
    ))


def read_file_content(path):
    with open(path, 'rb') as inputfile:
        data = inputfile.read()
    return data


def md5(path):
    data = read_file_content(path)

    md5_digest = hashlib.md5(data).hexdigest()
    return md5_digest


def upload(file_path, target_path):
    ret, info = bucket.stat(QINIU_BUCKET, target_path)
    # print("-----------qiniu-----------")
    # print(ret)
    # print(info)
    # print("-----------qiniu end-----------")

    if info.status_code == 200:
        print("file exist,success upload")
    else:
        token = q.upload_token(QINIU_BUCKET, target_path, 3600)
        ret, info = put_file(token, target_path, file_path)
        url = QINIU_DOMAIN + "/" + target_path
        print("success upload:" + url)
        return ret, info


def get_all_files(folder_path):
    """
    遍历文件夹，找出所有的文件路径
    :param folder_path:文件夹路径
    :return:路径数组
    """
    FILE_PATHS = []
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        for f in filenames:
            if not f.endswith(".mp3") and not f.endswith(".cache.json") \
                    and not f.endswith(".manifest.json"):
                file_path = os.path.join(dirpath, f)
                FILE_PATHS.append(file_path)
    return FILE_PATHS


def read_cache_from_disk(config):
    global cache
    cache_path = config.cache_path()
    if os.path.exists(cache_path):
        try:
            data = json.loads(read_file_content(cache_path))
        except Exception, e:
            data = {"md5_map": {}}
        cache = data.get("md5_map", {})
        # print("read_cache_from_disk", cache)
    else:
        cache = {}


def write_file(content, file_name):
    with open(file_name, 'wb+') as f:
        f.write(content.encode('utf-8'))


def write_cache(config, data):
    obj = {"md5_map": data}
    write_file(json.dumps(obj), config.cache_path())


def write_manifest(config, data):
    manifest = {}
    for path in data:
        f_name, suffix = os.path.splitext(path)
        dirname = os.path.dirname(path)
        manifest[path] = dirname + "/" + str(data[path]["md5"]) + suffix

    write_file(json.dumps(manifest), config.manifest_path())


def get_file_md5(config):
    cache_map = {}
    work_path = config.WORK_PATH
    files_paths = get_all_files(work_path)
    for path in files_paths:
        rpath = os.path.relpath(path, work_path)
        md5_str = md5(path)
        cache_map[rpath] = {"md5": md5_str}
    return cache_map


def main(config):
    global cache

    cdn_path = config.TARGET_CDN_PATH
    work_path = config.WORK_PATH

    # 初始化
    if config.INIT:
        files_paths = get_all_files(work_path)
        cache_map = {}

        for path in files_paths:
            fd = FileDescriptor(work_path=work_path, compress=True, path=path, cache=cache_map)

            if cdn_path:
                fd.upload()
        write_cache(config, cache_map)
        write_manifest(config, cache_map)
        print("init success")
    else:
        files_paths = get_all_files(work_path)
        read_cache_from_disk(config)

        for path in files_paths:
            fd = FileDescriptor(work_path=work_path, path=path, cache=cache)
            fd.update_cache()

            if config.COMPRESS:
                fd.compress()

            if config.TARGET_CDN_PATH:
                fd.upload()

        write_cache(config, cache)
        write_manifest(config, cache)

        print("上传manifest路径：")
        upload(config.manifest_path(), "manifest/" + str(int(time.time())) + ".json")


class FileDescriptor():
    def __init__(self, work_path, path, compress=False, cache={}):
        self.WORK_PATH = work_path
        self.PATH = path
        self.COMPRESS = compress
        self.UPLOADED = False
        self.CACHE = cache
        self.CACHE_MD5 = None
        self.MD5 = self.calc_md5()

        if not self.is_image():
            self.COMPRESS = True

        if cache.get(self.rel_path(), None):
            data = cache[self.rel_path()]
            self.COMPRESS = data["compress"]
            self.UPLOADED = data["uploaded"]
            self.CACHE_MD5 = data['md5']
        else:
            self.update_cache()

    def is_image(self):
        return self.suffix().upper() in ['.PNG', ".JPG", ".JPEG"]

    def calc_md5(self):
        with open(self.PATH, 'rb') as inputfile:
            data = inputfile.read()
            md5_digest = hashlib.md5(data).hexdigest()
            return md5_digest

    def suffix(self):
        f_name, suffix = os.path.splitext(self.rel_path())
        return suffix

    def rel_path(self):
        return os.path.relpath(self.PATH, self.WORK_PATH)

    def need_compress(self):
        if self.suffix().upper() == ".PNG":
            if not self.CACHE_MD5:
                return True
            else:
                if self.MD5 == self.CACHE_MD5:
                    if self.COMPRESS:
                        return False
                    else:
                        return True
                else:
                    return True
        else:
            return False

    def compress(self):
        if self.need_compress():
            compress_png(self.PATH)
            self.MD5 = self.calc_md5()
            self.COMPRESS = True
            self.update_cache()

            # self.CACHE[self.rel_path()]["compress"] = True

    def upload_path(self):
        dirname = os.path.dirname(self.rel_path())
        upload_path = dirname + "/" + self.MD5 + self.suffix()
        return upload_path

    def upload(self):
        upload(self.PATH, self.upload_path())
        self.UPLOADED = True
        self.update_cache()
        # self.CACHE[self.rel_path()]["uploaded"] = True

    def json_obj(self):
        return {"md5": self.MD5, "uploaded": self.UPLOADED, "compress": self.COMPRESS}

    def update_cache(self):
        data = self.CACHE.get(self.rel_path(), None)
        if data:
            data["compress"] = self.COMPRESS
            data["uploaded"] = self.UPLOADED
            data["md5"] = self.MD5
        else:
            self.CACHE[self.rel_path()] = self.json_obj()


class Config():

    def __init__(self, args):
        self.WORK_PATH = args.work_path
        self.TARGET_CDN_PATH = args.target_cdn_path
        self.INIT = args.init
        self.COMPRESS = args.compress

    def manifest_path(self):
        return os.path.join(self.WORK_PATH, ".manifest.json")

    def cache_path(self):
        return os.path.join(self.WORK_PATH, ".cache.json")

    def remove_cache(self):
        if self.cache_exist():
            os.remove(self.cache_path())

    def remove_manifest(self):
        if self.manifest_exist():
            os.remove(self.manifest_path())

    def cache_exist(self):
        return os.path.exists(self.cache_path())

    def manifest_exist(self):
        return os.path.exists(self.manifest_path())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="版本控制脚本，压缩并上传到七牛")

    parser.add_argument("work_path", help="工作文件夹绝对路径")
    parser.add_argument("-t", "--target_cdn_path", help="七牛CDN路径")
    parser.add_argument("-i", "--init", help="初始化,会删除并重建缓存文件", action="store_true", )
    parser.add_argument("-c", "--compress", help="根据缓存，检查md5变化的文件并使用压缩", action="store_true")

    # parser.add_argument("target_path", type=str, help="CDN目标路径")

    args = parser.parse_args()

    c = Config(args)

    if not c.INIT:
        if not c.cache_exist() or not c.manifest_path():
            c.remove_cache()
            c.remove_manifest()
            raise Exception("use -i to init")

    main(Config(args))
    # main("/Users/peterpuppy/code/TestQQQ/release/wxgame", "testqqq")
    # main("/Users/peterpuppy/code/client_zuma/sylvanas/release/scr_compress", "zuma")
    # main("/Users/peterpuppy/code/TestTTT/release/wxgame", "test2")

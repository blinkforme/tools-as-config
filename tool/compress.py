# -*- coding: utf-8 -*-


import os
from multiprocessing.dummy import Pool as ThreadPool

import tinify

API_KEYS = [
    "FX9lrsc1h9ct8eH3LeeH3sFhDw68PtsV",  # Foxmail
    "2pejTbKzD7VhxgrWcbRjiMeTb0eEZkbx",  # 163邮箱
    "2XlrTo2oRLdhPaRxo71J8UPeJ5fcRTWe",  # gmail邮箱
    "7GmWlZOZJ0mjBVPWX9ExElNqz0XYQDq8",  # diye 163邮箱
    "6XQFKpolEJQKw7Qx7elpchvEcVudvYfn",  # 黄刚 163邮箱
    "qKEbo0Iwod0zHaS43sR4TM4ByQJWOYTB",  # 大刚
    "nsJOH9uvowE2KAZXK4Ir02D1zFXl89C8",  # 曹静
    "rcnvWw7clC2RbqbzrL3i38OUXbfNn8lY",  # 大刚2
    "UTfpG9C3nuP70wzz0UWyxzgVUEdGbDFn",  # 晓亮
    "PhXZtfxrybxMDUxj33j7BchRepfnEWlI",  # 子航
    "ZmhfvnkC0Y4AlPHzfFKPB3B3gllRnyWw",  # 刘文林
    "DrI0ILRARz8cD4kazHw1ZwZEdt2wDvFL",  # 齐晨
]

# ------CONFIG--------

# 不压缩路径
EX_COMPRESS_PATH = [
    "res/atlas/ui/common_ex.png"
    # "ui\\common_e\\bg_orange.png",
    # "ui\\common_e\\bg_pink.png",
    # "ui\\common_e\\icon_item.png",
    # "ui\\common_e\\ku.png",
    # "ui\\war\\purple.png",
    # "ui\\war\\tiaowen.png",
    # "ui\\war\\yellow.png",
]

# 压缩根目录



ABS_PATH = "C:\\Users\liangxiaoliang\\Desktop\\client_happy\\abbey\\release\\layaweb\\scr_compress"
# ABS_PATH = "/Users/peterpuppy/code/client_overseas/abbey/release/layaweb/scr_compress"
# ABS_PATH = "D:\\Cat\\gitAssetsDownload\\client\\trials\\release\\layaweb\\trials-v-7-20-4-compress"

# TinyPng 密钥
API_INDEX = 11

# 压缩目录
PATHS = [
    # "res/atlas/ui",
    # "res/atlas/ani",
    # "spine",
	 "spine_TH",
    # "ui",
    # "scene",
    # "3dres"
]

# ------END CONFIG--------

tinify.key = API_KEYS[API_INDEX]
PNG_PATHS = []
pool = ThreadPool(processes=10)


def next_key():
    global API_INDEX
    API_INDEX = API_INDEX + 1
    if API_INDEX >= len(API_KEYS):
        print("没有可以使用的KEY")
        return False
    tinify.key = API_KEYS[API_INDEX]
    return True


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def is_on_fucking_window():
    return os.name == 'nt'


def is_ex_filepath(path):
    """
    判断是否为压缩路径
    :param path:
    :return:
    """
    if is_on_fucking_window():
        return False
    else:
        for p in EX_COMPRESS_PATH:
            if os.path.samefile(path, os.path.join(ABS_PATH, p)):
                return True
        return False


def get_pngs(folder_path):
    """
    遍历文件夹，找出所有的PNG的绝对路径
    :param folder_path:文件夹路径
    :return:路径数组
    """
    paths = []
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        for f in filenames:
            if f.endswith(".png"):
                png_path = os.path.join(dirpath, f)

                if not is_ex_filepath(png_path):
                    paths.append(png_path)
                else:
                    print(u"该路径不压缩：" + png_path)

    PNG_PATHS.extend(paths)
    return paths


total = 0
before_total_size = 0.0
after_total_size = 0.0


def compress_png(path):
    """
    压缩一张图片
    :param path:
    :return:
    """
    global total
    global before_total_size
    global after_total_size

    total = total + 1

    before_size = os.path.getsize(path)
    before_total_size = before_total_size + before_size
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

            print(bcolors.OKBLUE + "压缩失败，第二次，请手工压缩：" + path + bcolors.ENDC)

    after_size = os.path.getsize(path)
    after_total_size = after_total_size + after_size

    bgcolor = bcolors.OKGREEN
    if after_size > 60000:
        bgcolor = bcolors.WARNING

    print(bgcolor + "压缩成功({path})，压缩{before_size}KB =>{after_size}KB,压缩 {reduce}%".format(
        before_size=before_size / 1000,
        after_size=after_size / 1000, path=path,
        reduce=round(float(before_size - after_size) / before_size, 2) * 100
    ) + bcolors.ENDC)


def process_pngs():
    global total
#    print("压缩开始")

    pool.map(compress_png, PNG_PATHS)

    print("-----------------------------------------")
    print("压缩结束，共压缩 {total} 个文件".format(total=total))
    print("原始总文件大小：{:10.4f}MB".format(before_total_size / (1024 * 1024)))
    print("压缩后总文件大小：{:10.4f}MB".format(after_total_size / (1024 * 1024)))
    print("总压缩比:{:10.2f}".format(after_total_size / before_total_size))


def main():
    for path in PATHS:
        get_pngs(os.path.join(ABS_PATH, path))

    process_pngs()


if __name__ == '__main__':
    main()

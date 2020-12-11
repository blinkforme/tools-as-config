# -*- coding: utf-8 -*-
from qiniu import Auth, put_file, etag
import os, sys, time

# 七牛
QINIU_ACCESSKEY = 'b67u1ysMlZLUzT43FRArPP7I6xOuwQbWUJOAm-ed'
QINIU_SECRETKEY = 'RBAWG1VQGeSn_OON6SUmE18E49n7WoaxlDyedVJ7'
QINIU_BUCKET = 'h5sq'
QINIU_DOMAIN = 'https://sq-img.jjhgame.com'

# 构建鉴权对象
q = Auth(QINIU_ACCESSKEY, QINIU_SECRETKEY)

if __name__ == '__main__':
    project_name = ""
    if len(sys.argv) > 1:
        project_name = sys.argv[1]

    project_is_exist = os.path.exists(os.path.join(os.path.curdir, "resource", project_name))

    if not project_is_exist:
        print("project not exist")

    # 生成上传 Token，可以指定过期时间等
    key = "config/" + project_name + "/" + str(time.time()) + ".json"
    token = q.upload_token(QINIU_BUCKET, key, 3600)
    localfile = './product/' + project_name + "/config.json"

    ret, info = put_file(token, key, localfile)

    print(info)
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)

    url = QINIU_DOMAIN + "/" + key
    print("success upload,url is:")

    print(url)

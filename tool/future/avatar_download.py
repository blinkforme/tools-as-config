# -*- coding: utf-8 -*-

import json
import urllib

with open('avatar.json') as fp:
    names = json.loads(fp.read())

num = 0
for x in names:
    try:
        f = open("images/" + str(num) + ".png", 'wb')
        f.write(urllib.urlopen(x).read())
        f.close()
        print("下载" + str(num))
        num = num + 1
    except Exception,e:
        print ("error:" + str(num))



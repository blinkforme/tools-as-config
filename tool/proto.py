# -*- coding: utf-8 -*-

import os
import sys

PROJECT_PATH = os.getcwd()
APPS_PATH = os.path.dirname(PROJECT_PATH)
sys.path.extend([PROJECT_PATH, APPS_PATH])
from tool.proto_to_as3 import str_to_as3_proto_s2c_class, render_register
from tool.proto.PbParser import PbParser
from tool.assassin import write_file

PROTO_SERVER_PATHS = []
PROTO_AS_PATHS = []

TARGET_PROTO_PATH = ""


def exec_cmd(cmd):
    return os.system(cmd)


def delete_all_old_proto_file(walk_path):
    for (dirpath, dirnames, filenames) in os.walk(walk_path):
        for f in filenames:
            path = os.path.join(walk_path, f)
            os.remove(path)


def get_all_protos():
    walk_path = TARGET_PROTO_PATH
    paths = []
    for (dirpath, dirnames, filenames) in os.walk(walk_path):
        for f in filenames:
            if not f.startswith('~') and not f.startswith('.'):
                paths.append(os.path.join(walk_path, f))

    return paths


def export_proto_as3(as3_proto_path):
    PROTO_FILE_NAMES = get_all_protos()

    parser = PbParser()

    print("start parsing")
    for path in PROTO_FILE_NAMES:
        with open(path, "r") as f:
            content = f.read()
            parser.parse(content=content, fileName=f.name)

    print("success generate AST")

    ast = parser.ast

    delete_all_old_proto_file(as3_proto_path)
    for index, key in enumerate(ast.messages):
        message = ast.messages[key]

        content = str_to_as3_proto_s2c_class(message=message)

        write_file(content, os.path.join(as3_proto_path, message.name + ".as"))

    print("success generate AS3 class files")

    register_content = render_register(messages=ast.messages.values())
    write_file(register_content, os.path.join(as3_proto_path, "ProtoClassRegister.as"))
    print("success generate AS3 register class ")
    print(u"导出客户端代码成功")


def export_proto_lua(server_proto_path, proto_path):
    """
    导出服务端proto文件
    :param server_proto_path: 服务器导出路径
    :param proto_path: proto文件存放路径
    :return:
    """
    cmd = "protoc -o {SERVER_PROTO_PATH}/abbey.pb  {PROTO_PATH}/*.proto".format(
        SERVER_PROTO_PATH=server_proto_path,
        PROTO_PATH=proto_path
    )
    print("exec cmd:")
    print(cmd)
    print("using google protoc")
    re = exec_cmd(cmd=cmd)

    if re == 0:
        print(u"导出服务端成功：" + "{SERVER_PROTO_PATH}/abbey.pb".format(SERVER_PROTO_PATH=server_proto_path))
    else:
        raise Exception("protoc 导出服务器pb失败")
        print(u"导出服务端失败")


def export_proto_js():
    pass


if __name__ == '__main__':

    project_name = ""

    if len(sys.argv) > 1:
        project_name = sys.argv[1]

    names = ['abbey', "trials", "trials-weibo", 'qqdt', 'abbey_3d', 'abbey_os', 'test']
    if project_name not in names:
        raise Exception("参数错误，必须为" + '|'.join(names))

    import importlib

    config = importlib.import_module('resource.' + project_name + '.config')

    PROTO_SERVER_PATHS = getattr(config, "PROTO_SERVER_PATHS")
    PROTO_AS_PATHS = getattr(config, "PROTO_AS_PATHS")

    CUR_PATH = os.path.dirname(__file__)

    # 目标proto文件夹路径
    TARGET_PROTO_PATH = os.path.join(CUR_PATH, "resource", project_name, "protos")

    for path in PROTO_SERVER_PATHS:
        export_proto_lua(server_proto_path=path, proto_path=TARGET_PROTO_PATH)

    for path in PROTO_AS_PATHS:
        export_proto_as3(as3_proto_path=path)

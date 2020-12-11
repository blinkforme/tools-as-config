# -*- coding: utf-8 -*-



def append_file(content, file_name):
    with open(file_name, 'a') as f:
        f.write(content)


def write_file(content, file_name):
    with open(file_name, 'wb+') as f:
        f.write(content.encode('utf-8'))

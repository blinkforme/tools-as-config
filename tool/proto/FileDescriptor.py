# -*- coding: utf-8 -*-


class PbFileDescriptor():
    ''' 协议文件
    '''

    def __init__(self, fileName, fullPath):
        self.fileName = fileName
        self.fullPath = fullPath
        self.includes = []

    def addInclude(self, fd):
        if fd.isFDExist(self): return False  # 循环包含

        self.includes.append(fd)
        return True

    def isFDExist(self, fd):
        if fd == self or fd.fileName == self.fileName: return True
        for inc in self.includes:
            if inc.isFDExist(fd): return True
        return False

    def findType(self, name):
        try:
            return self.types[name]
        except:
            pass

        for fd in self.includes:
            code = fd.findType(name)
            if code:
                return code

        return None

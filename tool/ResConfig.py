# -*- coding: utf-8 -*-
import sys, os, importlib, json


class ResConfig:
    def __init__(self, res_path):
        self.resource_path = res_path

        # sys.path.extend([self.resource_path])
        sys.path.insert(0,self.resource_path)
        config = importlib.import_module('config')
        sys.path.remove(self.resource_path)

        self.TARGET_PATHS = getattr(config, "TARGET_PATHS", [])

        self.FIRST_CONFIG = getattr(config, "FIRST_CONFIG", [])

        self.AS3_CLAZZ_TARGET_PATHS = getattr(config, "AS3_CLAZZ_TARGET_PATHS", [])

        self.SERVER_PATH = getattr(config, "SERVER_PATH", None)
        self.JSON_SERVER_PATH = getattr(config, "JSON_SERVER_PATH", None)

        self.CONFIG_MANAGER_PATH = getattr(config, "CONFIG_MANAGER_PATH", "manager")

        self.IS_LANG_TEMPLATE = getattr(config, "IS_LANG_TEMPLATE", False)

        self.IS_FUNK_TEMPLATE = getattr(config, "IS_FUNK_TEMPLATE", False)

        self.EXCEL_PATH = self.resource_path + '/excels/'

        self.BASE_ON = getattr(config, "BASE_ON", None)
        self.EXCEL_FILE_NAMES = self.get_all_excels()

        self.UNITY_PATH = getattr(config, "UNITY_PATH", None)

    def _get_all_excels_from_path(self, walk_path):
        paths = []
        for (dirpath, dirnames, filenames) in os.walk(walk_path):
            for f in filenames:
                if not f.startswith('~') and not f.startswith('.'):
                    paths.append(os.path.join(walk_path, f))
        return paths

    def exist_filename(self, paths, filename):
        for i, path in enumerate(paths):
            if os.path.basename(path) == filename:
                return i
        return -1

    def get_all_excels(self):

        base_on_paths = []
        if self.BASE_ON:
            base_on_paths = self._get_all_excels_from_path(self.BASE_ON + "/excels/")

        excel_paths = self._get_all_excels_from_path(self.EXCEL_PATH)

        for i, path in enumerate(excel_paths):
            filename = os.path.basename(path)
            index = self.exist_filename(base_on_paths, filename)
            if index >= 0:
                base_on_paths[index] = path
            else:
                base_on_paths.append(path)
        return base_on_paths

    def create_folder(self):
        """
        创建路径
        :return:
        """
        if self.TARGET_PATHS:
            for path in self.TARGET_PATHS:
                if not os.path.exists(path):
                    os.makedirs(path)
        if self.AS3_CLAZZ_TARGET_PATHS:
            for path in self.AS3_CLAZZ_TARGET_PATHS:
                if not os.path.exists(path):
                    os.makedirs(path)

        if self.SERVER_PATH and not os.path.exists(self.SERVER_PATH):
            os.makedirs(self.SERVER_PATH)

        if self.JSON_SERVER_PATH and not os.path.exists(self.JSON_SERVER_PATH):
            os.makedirs(self.JSON_SERVER_PATH)

# -*- coding: utf-8 -*-
__author__ = "yangtao"
__version__ = '1.1'

import sys
import os
import threading as td

from PySide2 import QtWidgets
from PySide2 import QtCore

from .import welcome
from .core import file_packaging as fp
from .ui.main_ui import Mian_Widget


class Signal_Wrapper(QtCore.QObject):
    add_info = QtCore.Signal(str)
    set_pack_button_enabled = QtCore.Signal(bool)
    #set_dl_value = QtCore.Signal(int)
    set_files_process_value = QtCore.Signal(int)
    def __init__(self):
        super(Signal_Wrapper, self).__init__()


class Main(Mian_Widget):
    def __init__(self):
        super(Main, self).__init__()
        self.signal_wrapper = Signal_Wrapper()

        self.drives_name = []

        # 连接信号和槽
        # 连接 打包
        self.pack_widget.start_button.clicked.connect(self.__start_pack_thread)
        # 设置解包路径映射
        self.unpack_widget.resolve_button.clicked.connect(self.set_unpak_map)
        # 连接 解包
        self.unpack_widget.start_button.clicked.connect(self.__start_unpack_thread)
        # 添加运行信息
        self.signal_wrapper.add_info.connect(self.add_info)
        # 设置关闭开启打包按钮
        self.signal_wrapper.set_pack_button_enabled.connect(self.set_button_enabled)
        # # 进度条
        # self.signal_wrapper.set_dl_value.connect(self.dl_progressbar.setValue)
        # 文件进度
        self.signal_wrapper.set_files_process_value.connect(self.files_process)

        try:
            self.add_info(welcome.ascii_cat, False)
        except:
            pass

    def set_unpak_map(self):
        pack_dir = self.unpack_widget.pack_dir_edit.text()
        if os.path.isdir(pack_dir):
            self.drives_name = fp.get_root_name(pack_dir)
            self.unpack_widget.add_map(self.drives_name)
        else:
            self.unpack_widget.remove_map()

    def __start_unpack_thread(self):
        tr = td.Thread(target=self.start_unpack)
        tr.start()

    def start_unpack(self):
        print("START\n")

        self.signal_wrapper.set_pack_button_enabled.emit(False)
        self.signal_wrapper.add_info.emit("正在解包，请稍后...")

        drives_map_status = True
        unpack_message = []
        drives_map = self.unpack_widget.get_map(self.drives_name)
        for d_map in drives_map:
            value = drives_map[d_map]
            if not value or not os.path.isdir(value):
                self.signal_wrapper.add_info.emit("[%s] 对应了一个错误的路径" % d_map)
                drives_map_status = False
            else:
                drives_map[d_map] = drives_map[d_map].replace("\\", "/")
                unpack_message.append("%s >>> %s" % (d_map, value))

        if drives_map_status:
            pk_folder = self.unpack_widget.pack_dir_edit.text()
            new_files = fp.unpack(pk_folder,
                                  root_map=drives_map,
                                  files_process_hook=self.signal_wrapper.set_files_process_value.emit)
            for f in new_files:
                unpack_message.append("[%s] >>> %s" % (os.path.basename(f), f))

            unpack_message = "\n".join(unpack_message)
            self.signal_wrapper.add_info.emit(unpack_message)

        self.signal_wrapper.set_pack_button_enabled.emit(True)
        self.signal_wrapper.add_info.emit("结束")

        print("\nDONE")

    def __start_pack_thread(self):
        tr = td.Thread(target=self.start_pack)
        tr.start()

    def start_pack(self):
        print("START\n")

        self.signal_wrapper.set_pack_button_enabled.emit(False)

        project_file = self.pack_widget.file_name_edit.text()
        export_dir = self.pack_widget.export_dir_edit.text()

        if not os.path.isfile(project_file):
            text = "工程文件不存在 %s" % project_file
            print(text)
            self.signal_wrapper.add_info.emit(text)
            project_file = None
        else:
            project_file = project_file.replace("\\", "/")
        if not os.path.isdir(export_dir):
            text = "输出路径不存在 %s" % export_dir
            print(text)
            self.signal_wrapper.add_info.emit(text)
            export_dir = None
        else:
            export_dir = export_dir.replace("\\", "/")

        if project_file and export_dir:
            # 针对不同格式文件添加忽略路径
            if project_file.endswith(".nk"):
                ignore_paths = [".+/Nuke\d+\..+/nuke-.+\.dll"]
            else:
                ignore_paths = []

            file_pure_name = os.path.splitext(os.path.basename(project_file))[0]
            export_dir = os.path.join(export_dir, file_pure_name).replace("\\", "/")
            # 创建导出目录
            if not os.path.exists(export_dir):
                try:
                    os.makedirs(export_dir)
                except Exception as e:
                    print(e)
                    self.signal_wrapper.add_info.emit(text)
                    return

            self.signal_wrapper.add_info.emit("工程文件：%s" % project_file)
            self.signal_wrapper.add_info.emit("输出目录：%s" % export_dir)
            self.signal_wrapper.add_info.emit("正在打包，请稍后...")
            pack_info = fp.pack(project_file,
                                export_dir,
                                ignore_paths=ignore_paths,
                                files_process_hook=self.signal_wrapper.set_files_process_value.emit)
            if pack_info:
                result = fp.util.generate_log_lines(pack_info)
            else:
                result = ""
            self.signal_wrapper.add_info.emit(result)
            files_floder = "%s/%s" % (export_dir, fp.config.FILES_FLODER_NAME)
            res_floder = "%s/%s" % (export_dir, fp.config.RES_FLODER_NAME)
            self.signal_wrapper.add_info.emit("工程文件在：%s\n资产文件在：%s" % (files_floder, res_floder))

        self.signal_wrapper.set_pack_button_enabled.emit(True)
        self.signal_wrapper.add_info.emit("结束")

        print("\nDONE")


def show():
    welcome.show()
    app = QtWidgets.QApplication()
    main = Main()
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    show()
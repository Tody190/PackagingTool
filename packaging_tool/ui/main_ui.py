# -*- coding: utf-8 -*-
__author__ = "yangtao"

import sys
import datetime
import os

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore


class DropLineEdit(QtWidgets.QLineEdit):
    def __init__(self):
        super(DropLineEdit, self).__init__()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(DropLineEdit, self).dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url_object = event.mimeData().urls()[0]
            self.setText(url_object.toLocalFile())
        else:
            super(DropLineEdit, self).dropEvent(event)


class Unpack_Widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Unpack_Widget, self).__init__(parent=parent)
        self.setWindowTitle("释放")
        self.setMinimumWidth(400)

        self.pack_dir_edit = DropLineEdit()
        self.pack_dir_edit.setPlaceholderText("输入“包文件”夹路径")
        self.resolve_button = QtWidgets.QPushButton("解析")
        self.pack_dir_layout = QtWidgets.QHBoxLayout()
        self.pack_dir_layout.addWidget(self.pack_dir_edit)
        self.pack_dir_layout.addWidget(self.resolve_button)

        self.map_layout = QtWidgets.QFormLayout()

        # 开始
        self.start_button = QtWidgets.QPushButton("释放")
        self.start_button.setEnabled(False)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(self.pack_dir_layout)
        self.main_layout.addLayout(self.map_layout)
        self.main_layout.addWidget(self.start_button)

        self.start_button.clicked.connect(lambda: self.close())

    def get_map(self, map_label):
        drives_map = {}
        for l in map_label:
            value = self.findChild(DropLineEdit, l).text()
            drives_map[l] = value
        return drives_map

    def add_map(self, map_label):
        self.remove_map()
        if map_label:
            for l in map_label:
                label = QtWidgets.QLabel("%s >>> " % l)
                edit = DropLineEdit()
                edit.setObjectName(l)
                self.map_layout.addRow(label, edit)
            self.start_button.setEnabled(True)

    def remove_map(self):
        for row in range(self.map_layout.rowCount()):
            self.map_layout.removeRow(0)
        self.start_button.setEnabled(False)


class Pack_Widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Pack_Widget, self).__init__(parent=parent)
        self.setWindowTitle("打包")
        self.setMinimumWidth(400)

        file_name_label = QtWidgets.QLabel("工程文件")
        self.file_name_edit = DropLineEdit()
        export_dir_label = QtWidgets.QLabel("输出路径")
        self.export_dir_edit = DropLineEdit()

        # 开始
        self.start_button = QtWidgets.QPushButton("打包")

        self.main_layout = QtWidgets.QFormLayout(self)
        self.main_layout.addRow(file_name_label, self.file_name_edit)
        self.main_layout.addRow(export_dir_label, self.export_dir_edit)
        self.main_layout.addRow(self.start_button)

        self.start_button.clicked.connect(lambda: self.close())


class Mian_Widget(QtWidgets.QWidget):
    def __init__(self):
        super(Mian_Widget, self).__init__()
        self.settings = QtCore.QSettings("HZ", "find_ver")

        self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_TitleBarCloseButton))
        self.setWindowTitle("通用工程打包工具 by YangTao")
        self.setMinimumWidth(485)

        # 当前信息框显示的内容
        self.current_info = ""

        # # 进度条
        # self.dl_progressbar = QtWidgets.QProgressBar()
        # self.dl_progressbar.setTextVisible(False)

        # 信息框
        self.info_edit = QtWidgets.QTextEdit()
        self.info_edit.setWordWrapMode(QtGui.QTextOption.NoWrap)

        # 打包，释放按钮
        self.pack_button = QtWidgets.QPushButton("打包")
        self.pack_button.setObjectName("pack_project")
        self.pack_button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ArrowDown))
        self.unpack_button = QtWidgets.QPushButton("释放")
        self.unpack_button.setObjectName("unpack_project")
        self.unpack_button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ArrowUp))

        self.expand_button_layout = QtWidgets.QHBoxLayout()
        self.expand_button_layout.addWidget(self.pack_button)
        self.expand_button_layout.addWidget(self.unpack_button)

        # 打包，释放 UI
        self.pack_widget = Pack_Widget(self)
        self.unpack_widget = Unpack_Widget(self)
        # self.unpack_widget.add_map(["a", "b", "c", "d"])
        # self.unpack_widget.setHidden(True)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        # self.main_layout.addWidget(self.dl_progressbar)
        self.main_layout.addWidget(self.info_edit)

        self.main_layout.addLayout(self.expand_button_layout) \
            # connect
        self.pack_button.clicked.connect(self.show_pack_widget)
        self.unpack_button.clicked.connect(self.show_pack_widget)

    def set_button_enabled(self, status):
        self.pack_button.setEnabled(status)
        self.unpack_button.setEnabled(status)

    def add_info(self, text, add_time_line=True, new_line=True):
        if new_line:
            self.current_info = self.info_edit.toPlainText()
        if add_time_line:
            time_line = "%s:\n" % datetime.datetime.now().strftime("%H:%M:%S")
        else:
            time_line = ""
        current_info = self.current_info + time_line + text + "\n"
        if new_line:
            self.current_info = current_info
        self.info_edit.setText("%s" % current_info)
        self.info_edit.moveCursor(QtGui.QTextCursor.End)

    def files_process(self, value=None):
        if value:
            text = u"正在处理第[%s]个文件" % (str(value))
            self.add_info(text, new_line=False)

    def show_pack_widget(self):
        if self.sender().objectName() == "pack_project":
            self.pack_widget.show()
            self.unpack_widget.close()

        if self.sender().objectName() == "unpack_project":
            self.pack_widget.close()
            self.unpack_widget.show()

    def closeEvent(self, event):
        self.settings.setValue("mainwindow_geo", self.saveGeometry())


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    mw = Mian_Widget()
    mw.show()
    sys.exit(app.exec_())

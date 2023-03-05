# -*- coding: utf-8 -*-
__author__ = "yangtao"


import shutil
import os
import re

from . import util
from . import config


def file_replace_path(src_file, dst_file, map):
    # 生成路径映射表
    # 直接替换文件路径会出现 #### 这种情况，所以使用路径映射表替换
    dir_map = {}
    for original_file in map:
        original_dir = os.path.dirname(original_file)
        if not original_dir in dir_map:
            dir_map[original_dir] = os.path.dirname(map[original_file])

    new_file_info = ""
    # 读取文件
    with open(src_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f.readlines():
            line_path = re.search(config.FILE_PATH_RE, line)
            if line_path:
                line_path = os.path.dirname(line_path.group())
                if line_path in dir_map:
                    line = line.replace(line_path, dir_map[line_path])
                    new_file_info += line
                    continue
            new_file_info += line

    # 写入文件
    dst_file_dir = os.path.dirname(dst_file)
    if not os.path.exists(dst_file_dir):
        os.makedirs(dst_file_dir)
    with open(dst_file, "w", encoding="utf-8", errors="ignore") as f:
        f.write(new_file_info)


def file_comparison(path, file_metadata):
    if file_metadata:
        if path in file_metadata:
            if os.path.getsize(path) == file_metadata[path]["size"]:
                return True
    return False


def copy_file(src_file_path, dst_file_path):
    dst_dir_name = os.path.dirname(dst_file_path)
    if not os.path.exists(dst_dir_name):
        try:
            os.makedirs(dst_dir_name)
        except Exception as e:
            print(e)
    try:
        shutil.copy2(src_file_path, dst_file_path)
    except Exception as e:
        print(e)
    return True


def copy_files(paths_list,
               dst_folder,
               with_hierarchy=True,
               cover=False,
               ignore_files=None,
               verbose=True,
               files_process_hook=None):
    file_metadata = util.read_json(ignore_files)
    files_process_index = 0
    for path in paths_list:
        if files_process_hook:
            files_process_index += 1
            files_process_hook(files_process_index)

        if with_hierarchy:
            dst_file_path = util.add_root_path(dst_folder, path)
        else:
            dst_file_path = os.path.join(dst_folder, os.path.basename(path)).replace("\\", "/")

        if os.path.exists(dst_file_path):
            if os.path.getsize(path) == os.path.getsize(dst_file_path):
                if not cover:
                    util.add_log("FileExist", path)
                    continue

        copy_status = copy_file(path, dst_file_path)
        if copy_status:
            util.add_log("CopySuccess", path)
            if verbose:
                print("%s --> %s"%(path, dst_file_path))
            if file_metadata:
                file_metadata = util.add_file_metadata(path, file_metadata)
        else:
            util.add_log("ErrorCopy", path)
    if file_metadata:
        util.write_file_metadata_json(ignore_files, file_metadata)
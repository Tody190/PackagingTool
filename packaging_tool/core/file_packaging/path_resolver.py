# -*- coding: utf-8 -*-
__author__ = "yangtao"

import os
import re

from . import config
from . import util


def replace_path_root(path, root_map):
    # 根据映射表将路径头替换
    for original_root in root_map:
        if original_root.upper() == path[0].upper():
            return os.path.join(root_map[original_root], path[3:]).replace("\\", "/")


def match_path(path, match_part_list):
    for re_ex in match_part_list:
        if re.match(re_ex, path):
            return True
    return False


def file_find_paths(file_path, match_paths=None, ignore_paths=None):
    file_paths_list = []
    # file_path = file_path.replace("\\", "/")
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            re_result = re.search(config.FILE_PATH_RE, line)
            if re_result:
                re_result_path = re_result.group()
                # ignore path
                if ignore_paths:
                    if match_path(re_result_path, ignore_paths):
                        util.add_log("Ignore", re_result_path)
                        continue
                # match head
                if match_paths:
                    if not match_path(re_result_path, match_paths):
                        util.add_log("Ignore", re_result_path)
                        continue

                if re_result_path not in file_paths_list:
                    file_paths_list.append(re_result_path)
    return sorted(file_paths_list)


def path_find_sequence(file):
    file_path_list = []
    file_name = os.path.basename(file)
    root_path = os.path.dirname(file)

    if not os.path.isdir(root_path):
        return [file]

    # 匹配 udim 贴图
    re_name = file_name
    if "<UDIM>" in re_name:
        re_name = re_name.replace("<UDIM>", "[0-9]+")

    if "<udim>" in re_name:
        re_name = re_name.replace("<udim>", "[0-9]+")

    # 匹配 #### 序列路径
    seq_match_part = re.match(".+(\.|_)#+(\.|_).+", re_name)
    if seq_match_part:
        seq_num_search_part = re.search("#+", seq_match_part.group()).group()
        seq_num = len(seq_num_search_part)
        re_name = re_name.replace(seq_num_search_part, "[0-9]{%s}" % seq_num)

    # 匹配 xxxx.123.exr
    seq_match_part = re.match(".+(\.|_)[0-9]+(\.).+", re_name)
    if seq_match_part:
        seq_num_search_part = re.search("[0-9]+", seq_match_part.group()).group()
        re_name = re_name.replace(seq_num_search_part, "[0-9]+")

    # 匹配 $F123
    seq_search_part = re.search("\$F[0-9]+", file_name)
    if seq_search_part:
        seq_search_part = seq_search_part.group()
        seq_num = seq_search_part.replace("$F", "")
        re_name = file_name.replace(seq_search_part, "[0-9]{%s}" % seq_num)

    # 匹配 %04d
    seq_search_part = re.search("%([0-9]+)+d", file_name)
    if seq_search_part:
        seq_part = seq_search_part.group(0)
        seq_num = int(seq_search_part.group(1))
        re_name = file_name.replace(seq_part, "[0-9]{%s}" % seq_num)

    if re_name == file_name:
        return [file]
    else:
        for file in os.listdir(root_path):
            if re.match(re_name, file):
                file_path = os.path.join(root_path, file).replace("\\", "/")
                if file_path not in file_path_list:
                    file_path_list.append(file_path)

        if not file_path_list:
            return [file]

    return file_path_list


def path_find_same_name(path):
    """
    找到一个路径下命名相同格式不同的所有文件
    """
    file_name = os.path.basename(path)
    file_root_path = os.path.dirname(path).replace("\\", "/")
    startswith_part = file_name.rsplit(".", 1)[0]

    file_path_list = []
    for file in os.listdir(file_root_path):
        if file.startswith(startswith_part):
            file_path = os.path.join(file_root_path, file).replace("\\", "/")
            if file_path not in file_path_list:
                file_path_list.append(file_path)

    if file_path_list:
        return file_path_list
    else:
        return [path]

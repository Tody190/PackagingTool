# -*- coding: utf-8 -*-
__author__ = "yangtao"

import os
import pprint

from .path_resolver import file_find_paths
from .path_resolver import path_find_sequence
from .path_resolver import path_find_same_name
from .path_resolver import replace_path_root
from .file_process import copy_files
from .file_process import copy_file
from .file_process import file_comparison
from .file_process import file_replace_path
from .util import read_json
from .util import add_file_metadata
from .util import write_file_metadata_json
from .util import add_log
from .util import generate_copy_log
from .util import get_log
from . import config

__all__ = ["pack",
           "get_files_floder", "get_files_size", "dumps_ignore_files", "get_files"]


def get_files_floder(file_path_list, file_types=None, verbose=True):
    new_file_path_list = []
    for f in file_path_list:
        if os.path.isfile(f):
            if file_types:
                for t in file_types:
                    if f.endswith(t):
                        new_file_path_list.append(f)
            else:
                new_file_path_list.append(f)

    files_floder = []
    for f in new_file_path_list:
        path_folder = os.path.dirname(f)
        if path_folder not in files_floder:
            files_floder.append(path_folder)
            if verbose:
                print(path_folder)

    return files_floder


def get_files_size(files_list, verbose=True):
    def unit_conver(fize):
        if fize > 1024 ** 4:
            return "%s/TB" % (fize / float(1024 ** 4))
        if fize > 1024 ** 3:
            return "%s/GB" % (fize / float(1024 ** 3))
        if fize > 1024 ** 2:
            return "%s/MB" % (fize / float(1024 ** 2))
        return "%s/kB" % (fize / float(1024))

    files_size = {}
    all_files = sorted(list(set(files_list)))
    all_file_size = 0
    for f in all_files:
        fsize = os.path.getsize(f)
        files_size[f] = fsize
        if verbose:
            print(f, unit_conver(fsize))
        all_file_size += fsize

    files_size["all_files_size"] = all_file_size
    if verbose:
        print("All Files Size", unit_conver(all_file_size))
    return files_size


def dumps_ignore_files(paths_list, ignore_files):
    file_metadata = read_json(ignore_files)
    for path in paths_list:
        file_metadata = add_file_metadata(path, file_metadata)
    write_file_metadata_json(ignore_files, file_metadata)


def get_files(src_file, match_paths=[], ignore_paths=[], ignore_files=None,
              verbose=True, deep_find_level=0, deep_files_type=[]):
    if verbose:
        print("find paths in %s" % src_file)

    print(u"??????????????????...")
    # ???????????????????????????????????????
    files_list = file_find_paths(src_file, match_paths, ignore_paths)
    if verbose:
        print(u"??????????????????: ??????, [%s]" % str(len(files_list)))

    # ??????????????????
    print(u"??????????????????...")
    seq_files_list = []
    for f in files_list:
        seq_files_list += path_find_sequence(f)
    seq_files_list = list(set(seq_files_list))
    if verbose:
        print(u"??????????????????: ??????, [%s]" % str(len(seq_files_list)))

    # ????????????????????????????????????
    print(u"??????????????????...")
    exist_files_list = []
    for path in seq_files_list:
        if os.path.isfile(path) or os.path.isdir(path):
            exist_files_list.append(path)
    if verbose:
        print(u"??????????????????: ??????, [%s]" % str(len(exist_files_list)))

    # ??????????????????????????????????????????????????????
    print(u"??????????????????...")
    add_same_name_paths_list = []
    for path in exist_files_list:
        add_same_name_paths_list += path_find_same_name(path)
    add_same_name_paths_list = list(set(add_same_name_paths_list))
    if verbose:
        print(u"??????????????????: ??????, [%s]" % str(len(add_same_name_paths_list)))

    # ????????????
    if deep_find_level:
        print(u"????????????...")
        # add deep files
        need_deep_files = []
        for path in add_same_name_paths_list:
            for file_type in deep_files_type:
                if path.endswith(file_type):
                    if path not in need_deep_files:
                        need_deep_files.append(path)

        deep_paths_list = []
        if need_deep_files:
            ignore_paths = ignore_paths + add_same_name_paths_list
            deep_find_level = deep_find_level - 1
            for path in need_deep_files:
                if verbose:
                    print("Deeply find the reference file: %s" % os.path.basename(path))
                    deep_file_paths = get_files(path,
                                                verbose=verbose,
                                                ignore_paths=ignore_paths,
                                                deep_find_level=deep_find_level,
                                                match_paths=match_paths,
                                                ignore_files=None)
                    if deep_file_paths:
                        for deep_path in deep_file_paths:
                            if deep_path not in deep_paths_list:
                                deep_paths_list.append(deep_path)
                                ignore_paths.append(deep_path)
        deep_paths_list += add_same_name_paths_list
        if verbose:
            print(u"????????????: ??????, [%s]" % str(len(deep_paths_list)))
    else:
        deep_paths_list = add_same_name_paths_list

    # file comparison
    print(u"??????????????????????????????...")
    filter_ignore_paths_list = []
    file_metadata = read_json(ignore_files)
    if file_metadata:
        for path in deep_paths_list:
            if not file_comparison(path, file_metadata):
                filter_ignore_paths_list.append(path)
            else:
                add_log("FileExist", path)
    else:
        filter_ignore_paths_list = deep_paths_list
    if verbose:
        print(u"??????????????????????????????: ??????, [%s]" % str(len(filter_ignore_paths_list)))

    print(u"??????")
    return sorted(filter_ignore_paths_list)


def __get_pack_info(pk_folder):
    info = {config.FILES_FLODER_NAME: {},
            config.RES_FLODER_NAME: {}}

    for root, dirs, files in os.walk(pk_folder):
        for f in files:
            f_path = os.path.join(root, f).replace("\\", "/")
            for type in info.keys():
                start_path = os.path.join(pk_folder, type).replace("\\", "/")
                if f_path.startswith(start_path):
                    half_path = f_path.replace("%s/" % start_path, "")
                    original_path = "%s:%s" % (half_path[0], half_path[1:])
                    info[type][original_path] = f_path

    return info


def get_root_name(pk_folder):
    # ????????????????????????????????????
    root_path = []
    files_dir = os.path.join(pk_folder, config.FILES_FLODER_NAME)
    res_dir = os.path.join(pk_folder, config.RES_FLODER_NAME)
    for dir_path in [files_dir, res_dir]:
        if os.path.isdir(dir_path):
            for f in os.listdir(dir_path):
                type_dir_path = os.path.join(dir_path, f)
                if os.path.isdir(type_dir_path):
                    if f not in root_path:
                        root_path.append(f)
    return root_path


def unpack(pk_folder, root_map={}, verbose=True, files_process_hook=None):
    pk_folder = pk_folder.replace("\\", "/")
    pk_folder = util.remove_end_slash(pk_folder)

    def get_res_map(pack_dir, root_map):
        files_map = {}  # ???????????????????????????????????????
        for root, dirs, files in os.walk(pack_dir):
            for file_name in files:
                # ??????????????????????????????
                file = os.path.join(root, file_name).replace("\\", "/")
                file_split = file.split(pack_dir, 1)[-1].split("/", 2)
                # ?????????????????????
                origin_file_root = file_split[1]
                # ???????????????????????????????????????
                origin_file_no_root_part = file_split[2]
                # ??????????????????
                if origin_file_root in root_map:
                    files_map[file] = {"dst": "", "orig": ""}
                    dst_root_dir = root_map[origin_file_root]
                    dst_root_dir = util.remove_end_slash(dst_root_dir)
                    dst_file = os.path.join(dst_root_dir, origin_file_no_root_part).replace("\\", "/")
                    files_map[file]["dst"] = dst_file
                    origin_file = os.path.join("%s:/" % origin_file_root, origin_file_no_root_part)
                    files_map[file]["orig"] = origin_file
        return files_map

    # ??????????????????????????????????????????
    res_dir = os.path.join(pk_folder, config.RES_FLODER_NAME).replace("\\", "/")
    res_files_map = get_res_map(res_dir, root_map)
    if verbose:
        print("[copy src files]")

    files_process_index = 0
    for src_file in res_files_map:
        dst_file = res_files_map[src_file]["dst"]
        copy_status = copy_file(src_file, dst_file)
        if copy_status:
            copy_message = "%s --> %s" % (src_file, dst_file)
        if verbose:
            print(copy_message)
        if files_process_hook:
            files_process_index += 1
            files_process_hook(files_process_index)

    # ?????????????????????
    # ??????????????????????????????
    replace_map = {}
    for v in res_files_map.values():
        replace_map[v["orig"]] = v["dst"]
    # ???????????????
    if verbose:
        print("[copy src file]")
    files_dir = os.path.join(pk_folder, config.FILES_FLODER_NAME).replace("\\", "/")
    files_map = get_res_map(files_dir, root_map)

    new_files = []
    for src_file in files_map:
        dst_file = files_map[src_file]["dst"]
        print("[replace %s, wait...]" % dst_file)
        file_replace_path(src_file, dst_file, replace_map)
        new_files.append(dst_file)
        if verbose:
            print("%s --> %s" % (src_file, dst_file))

    return new_files


def pack(file, dst_folder, cover_copy=False, with_hierarchy=True, copy_itself=True,
         match_paths=[], ignore_paths=[], ignore_files=None,
         verbose=True, files_process_hook=None, deep_find_level=0, deep_files_type=[]):
    """
    file: str, ?????????????????????
    dst_folder: str, ???????????????
    cover_copy: bool, ?????????????????????????????????
    with_hierarchy: bool, ???????????????????????????
    match_paths: list, ????????????????????????????????????????????????????????????
    ignore_paths: list, ???????????????
    ignore_files: str, ?????? json ??????????????????????????????????????????????????????????????????????????????
    verbose: bool, ??????????????????
    deep_find_level???int, ???????????????????????????????????????????????????????????????????????????, 0 ????????????
    deep_files_type???lsit, ????????????????????????????????????????????????
    """
    if not os.path.isfile(file):
        raise Exception("'%s' not a file, or the file does not exist." % file)
        return
    if not os.path.isdir(dst_folder):
        raise Exception("'%s' not a folder, or the folder does not exist." % dst_folder)
        return

    # ????????????
    if copy_itself:
        file_dst_folder = os.path.join(dst_folder, config.FILES_FLODER_NAME).replace("\\", "/")
        copy_files([file], file_dst_folder,
                   verbose=verbose,
                   with_hierarchy=with_hierarchy,
                   ignore_files=ignore_files)

    be_copied_list = get_files(src_file=file,
                               match_paths=match_paths,
                               ignore_paths=ignore_paths,
                               ignore_files=ignore_files,
                               verbose=verbose,
                               deep_find_level=deep_find_level,
                               deep_files_type=deep_files_type)

    # ????????????
    resources_dst_folder = os.path.join(dst_folder, config.RES_FLODER_NAME).replace("\\", "/")
    copy_files(be_copied_list, resources_dst_folder,
               cover=cover_copy,
               with_hierarchy=with_hierarchy,
               ignore_files=ignore_files,
               verbose=verbose,
               files_process_hook=files_process_hook)

    # ????????????
    log_info = get_log()
    generate_copy_log(dst_folder, log_info)

    return log_info

# -*- coding: utf-8 -*-
__author__ = "yangtao"


import json
import re
import os
import time

from . import config


def get_current_time():
    return time.strftime(config.TIME_FORMAT, time.localtime(time.time()))


def add_root_path(root_path, file_path):
    if re.match(config.WIN_PATH_RE, file_path):
        return os.path.join(root_path, file_path.replace(":", "")).replace("\\", "/")
    else:
        return (root_path+file_path).replace("//", "/")


def add_log(type, path):
    if not type in config.log_info:
        config.log_info[type] = []
    if path not in config.log_info[type]:
        config.log_info[type].append(path)


def get_log():
    return config.log_info


def get_log_file():
    if os.path.exists(config.log_path):
        return config.log_path


def generate_log_lines(log_data):
    config.log_lines = ""
    for log_key in log_data:
        config.log_lines += "[%s]\n" % str(log_key)
        for l in log_data[log_key]:
            config.log_lines += str(l) + "\n"
    return config.log_lines


def generate_copy_log(path_folder, log_data):
    if os.path.isdir(path_folder):
        log_file_name = config.LOG_FILE_NAME.format(time=get_current_time())
        config.log_path = os.path.join(path_folder, log_file_name).replace("\\", "/")

        log_lines = generate_log_lines(log_data)
        with open(config.log_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(log_lines)
    else:
        raise Exception("'%s' not a folder, or the folder does not exist."%path_folder)


def add_file_metadata(path, file_metadata):
    if not file_metadata:
        file_metadata = {}
    file_metadata[path] = {"size": os.path.getsize(path)}
    return file_metadata


def remove_end_slash(the_str):
    if the_str:
        if the_str.endswith("/"):
            the_str = the_str.rsplit("/", 1)[0]
            return the_str
        elif the_str.endswith("\\"):
            the_str = the_str.rsplit("\\", 1)[0]
            return the_str
        else:
            return the_str
    else:
        return the_str


def read_json(json_path):
    if json_path and os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8", errors="ignore") as f:
            try:
                return json.loads(f.read())
            except:
                return {}
    return None


def write_file_metadata_json(json_path, file_metadata):
    if os.path.exists(json_path):
        current_time = get_current_time()
        os.rename(json_path, "%s(%s)"%(json_path, current_time))

    with open(json_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(json.dumps(file_metadata, **config.JSON_ARGS))


if __name__ == "__main__":
    the_str = "E:/"
    remove_end_slash(the_str)
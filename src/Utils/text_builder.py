# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 17:26
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : text_builder
# @Project : SecSec

def filename_filter(filename):
    """
    过滤文件名中的特殊字符
    :param filename: 文件名
    :return: 过滤后的文件名
    """
    special_char = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\t', '\r']
    for char in special_char:
        filename = filename.replace(char, ' ')
    return filename

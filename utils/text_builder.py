#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Project : SecCrawler 
@File    : text_builder
@desc    : 
@Author  : @Natro92
@Date    : 2024/7/25 上午2:22 
@Blog    : https://natro92.fun
@Contact : natro92@natro92.fun
"""
from colorama import Fore
from tqdm import tqdm


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


def beautify_md(text):
    """
    删除多个换行符，如果被反引号包裹，则不删除
    :param text: 文本
    :return: 美化后的文本
    """
    # 如果换行符超过五个，则删除只剩一个
    text = text.replace('0\n\n1\n\n2\n\n3\n\n4\n\n5\n\n6\n\n7\n\n8\n\n9', '\n')
    text = text.replace('\n\n\n\n', '\n')

    return text

def split_content(md_content, split_strings):
    """
    处理文本切割的函数
    :param md_content: 要切割的文本内容
    :param split_strings: 切割字符串列表
    :return: 切割后的文本内容
    """
    try:
        if all(s in md_content for s in split_strings):
            md_content = md_content.split(split_strings[0])[1].split(split_strings[1])[0]
        else:
            try:
                md_content = md_content.split(split_strings[0])[1]
            except IndexError:
                tqdm.write(Fore.YELLOW + '[?] Warn - 第一次切割失败' + Fore.RESET)
                try:
                    md_content = md_content.split(split_strings[1])[0]
                except IndexError:
                    tqdm.write(Fore.YELLOW + '[?] Warn - 第二次切割失败' + Fore.RESET)
    except Exception as e:
        tqdm.write(Fore.YELLOW + '[?] Warn - 内容切割失败' + Fore.RESET)
    return md_content
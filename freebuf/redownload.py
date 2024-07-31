#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Project : SecCrawler 
@File    : redownload
@desc    : 
@Author  : @Natro92
@Date    : 2024/7/26 下午3:33 
@Blog    : https://natro92.fun
@Contact : natro92@natro92.fun
"""
import os

from colorama import Fore
from tqdm import tqdm

from config import FILE_SAVE_PATH
from freebuf.freebuf import run_freebuf_crawler_by_id


def redownload():
    """
    根据文件里面每行文件名，删除一个，下载一个
    :return:
    """
    # * 判断文件是否存在
    if not os.path.exists('redownload.txt'):
        print(f'[*] Info - 未检测到 redownload.txt 已重新生成')
        exit(1)
    with open('redownload.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        run_freebuf_crawler_by_id(lines)
        tqdm.write(Fore.GREEN + f'[*] Info - Reload任务已完成' + Fore.RESET)

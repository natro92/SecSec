#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Project : SecCrawler 
@File    : files
@desc    : 
@Author  : @Natro92
@Date    : 2024/7/24 下午6:37 
@Blog    : https://natro92.fun
@Contact : natro92@natro92.fun
"""
import os

from config import FILE_SAVE_PATH


def is_image_folder_created(folder_name):
    """
    判断图片文件夹是否创建
    :return:
    """
    if not os.path.exists(os.path.join(FILE_SAVE_PATH, folder_name, 'images')):
        os.makedirs(os.path.join(FILE_SAVE_PATH, folder_name, 'images'))

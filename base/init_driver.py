#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Project : SecCrawler 
@File    : RUN_ME_FIRST
@desc    : 
@Author  : @Natro92
@Date    : 2024/7/25 上午1:10 
@Blog    : https://natro92.fun
@Contact : natro92@natro92.fun
"""
import os

from colorama import Fore
from toollib import autodriver

from config import DRIVER_PATH


def init_chrome():
    """
    初始化Chrome浏览器
    :return:
    """
    # 判断是否存在
    if os.path.exists(os.path.join(DRIVER_PATH)):
        print('[*] Info - 已初始化Chrome浏览器，请选择模式 ')
        exit(1)
    print('[*] Info - 正在初始化Chrome浏览器，请稍后... (配置文件约15MB，可以通过开启代理来加速下载)')
    driver_path = autodriver.chromedriver()
    print(Fore.GREEN + f'[*] Info - 已成功初始化，ChromeDriver路径: {driver_path}' + Fore.RESET)

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Project : SecCrawler 
@File    : main
@desc    : 
@Author  : @Natro92
@Date    : 2024/7/25 下午2:32 
@Blog    : https://natro92.fun
@Contact : natro92@natro92.fun
"""
import argparse
import os.path
from colorama import init, Fore, Style

from butian.butian import run_butian_crawler
from config import DRIVER_PATH
from freebuf.freebuf import run_freebuf_crawler
from base.init_driver import init_chrome
from freebuf.redownload import redownload
from xianzhi.xianzhi import run_xianzhi_crawler


def print_splash():
    print(f'''
    {Fore.CYAN}______{Fore.RESET}_____        {Fore.CYAN}____{Fore.RESET}______           
     {Fore.CYAN}____{Fore.RESET}  ___/____________  ___/___________
      {Fore.CYAN}__{Fore.RESET}____ \_  _ \  ___/____ \_  _ \  ___/
       {Fore.CYAN}_{Fore.RESET}___/ //  __/ /__ ____/ //  __/ /__  
       /____/ \___/\___/ /____/ \___/\___/  
                       @Natro92 - https://natro92.fun - natro92@natro92.fun
    ''')
    

def print_help():
    """
    打印帮助信息
    :return:
    """
    print(f'''
    {Fore.CYAN}______{Fore.RESET}_____        {Fore.CYAN}____{Fore.RESET}______           
     {Fore.CYAN}____{Fore.RESET}  ___/____________  ___/___________
      {Fore.CYAN}__{Fore.RESET}____ \_  _ \  ___/____ \_  _ \  ___/
       {Fore.CYAN}_{Fore.RESET}___/ //  __/ /__ ____/ //  __/ /__  
       /____/ \___/\___/ /____/ \___/\___/  
                    @Natro92 - https://natro92.fun - natro92@natro92.fun
Usage: SecSec.py [options]

Options:
-h, --help          显示帮助
-i, --init          初始化Chrome浏览器
-f, --freebuf       爬取FreeBuf文章
-x, --xianzhi       爬取先知社区文章
-b, --butian        爬取补天社区文章
-r, --reload        重新爬取某个文件，传入参数为社区名称如xianzhi、freebuf
    ''')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SecCrawler - 一个简单的安全爬虫')
    parser.add_argument('-i', '--init', action='store_true', help='初始化Chrome浏览器')
    parser.add_argument('-f', '--freebuf', action='store_true', help='爬取FreeBuf文章')
    parser.add_argument('-x', '--xianzhi', action='store_true', help='爬取先知社区文章')
    parser.add_argument('-b', '--butian', action='store_true', help='爬取补天文章')
    parser.add_argument('-r', '--reload', type=str, help='重新爬取')
    args = parser.parse_args()

    if args.init:
        init_chrome()
    if not os.path.exists(os.path.join(DRIVER_PATH)):
        init(autoreset=True)
        print(Fore.RED + '[!] Error - 请先进行初始化Chrome浏览器 -i ')
        exit(1)
    if args.freebuf:
        print_splash()
        print(Fore.CYAN + '[*] Info - 正在爬取 FreeBuf 文章...' + Fore.RESET)
        run_freebuf_crawler()
    if args.xianzhi:
        print_splash()
        print(Fore.CYAN + '[*] Info - 正在爬取 先知社区 文章...' + Fore.RESET)
        run_xianzhi_crawler()
    if args.butian:
        print_splash()
        print(Fore.CYAN + '[*] Info - 正在爬取 补天社区 文章...' + Fore.RESET)
        run_butian_crawler()
    if args.reload:
        print_splash()
        print(Fore.CYAN + '[*] Info - 正在重新下载文章...' + Fore.RESET)
        redownload()
    if not any(vars(args).values()):
        print_help()
        exit(1)

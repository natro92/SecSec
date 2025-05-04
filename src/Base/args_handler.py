# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 16:24
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : Args
# @Project : SecSec

import argparse

from colorama import Fore

from src.Crawler.Base.crawler_init import init_chrome
from src.Crawler.Freebuf.crawler_run import run_freebuf_crawler
from src.Crawler.Xianzhi.crawler_run import run_xianzhi_crawler
from src.Utils.log_manager import success


def print_splash():
    print(f'''
    {Fore.CYAN}______{Fore.RESET}_____        {Fore.CYAN}____{Fore.RESET}______           
     {Fore.CYAN}____{Fore.RESET}  ___/____________  ___/___________
      {Fore.CYAN}__{Fore.RESET}____ \\_  _ \\  ___/____ \\_  _ \\  ___/
       {Fore.CYAN}_{Fore.RESET}___/ //  __/ /__ ____/ //  __/ /__  
       /____/ \\___/\\___/ /____/ \\___/\\___/  
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
      {Fore.CYAN}__{Fore.RESET}____ \\_  _ \\  ___/____ \\_  _ \\  ___/
       {Fore.CYAN}_{Fore.RESET}___/ //  __/ /__ ____/ //  __/ /__  
       /____/ \\___/\\___/ /____/ \\___/\\___/  
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


def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
    parser.add_argument('-i', '--init', action='store_true', help='初始化Chrome浏览器')
    parser.add_argument('-f', '--freebuf', action='store_true', help='爬取FreeBuf文章')
    parser.add_argument('-x', '--xianzhi', action='store_true', help='爬取先知社区文章')
    parser.add_argument('-b', '--butian', action='store_true', help='爬取补天社区文章')
    parser.add_argument('-r', '--reload', type=str, help='重新爬取某个文件，传入参数为社区名称如xianzhi、freebuf')

    args = parser.parse_args()

    if args.help:
        print_help()
    elif args.init:
        print(success("初始化Chrome浏览器..."))
        init_chrome()
    elif args.freebuf:
        print("爬取FreeBuf文章...")
        run_freebuf_crawler()
    elif args.xianzhi:
        print("爬取先知社区文章...")
        run_xianzhi_crawler()
    elif args.butian:
        print("爬取补天社区文章...")
        # 调用爬取补天社区逻辑
    elif args.reload:
        print(f"重新爬取 {args.reload} 文件...")
        # 调用重新爬取逻辑
    else:
        print_splash()


if __name__ == '__main__':
    parse_args()

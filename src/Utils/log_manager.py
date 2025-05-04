# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 16:58
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : log_manager
# @Project : SecSec
from colorama import Fore


def success(msg):
    """
    打印成功信息
    :param msg:
    :return:
    """
    return Fore.GREEN + f'[*] Info - {msg}' + Fore.RESET


def fail(msg):
    """
    打印失败信息
    :param msg:
    :return:
    """
    return Fore.RED + f'[!] Info - {msg}' + Fore.RESET


def warn(msg):
    """
    打印警告信息
    :param msg:
    :return:
    """
    return Fore.YELLOW + f'[?] Info - {msg}' + Fore.RESET

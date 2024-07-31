#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Project : SecCrawler 
@File    : config
@desc    : 
@Author  : @Natro92
@Date    : 2024/7/24 下午6:36 
@Blog    : https://natro92.fun
@Contact : natro92@natro92.fun
"""

# * 基础设置
# driver路径
DRIVER_PATH = 'chromedriver.exe'
# 文件路径
FILE_SAVE_PATH = 'Outputs'
# 请求头
CRAWLER_HEADERS = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
]
# 每一页爬取后休眠时间
SLEEP_TIME = 4
# 休眠时间差
SLEEP_TIME_DELTA = 0.5
# 图片下载进程数
THREADS_NUM = 4

# * 爬虫设置
# ? FreeBuf 爬虫设置 -----
# FreeBuf 分类
FREEBUF_CATEGORY = ['web']
# 设置默认开始页
FREEBUF_PAGE_START = 1
# 设置默认结束页面
FREEBUF_PAGE_END = 308
# FREEBUF_CATEGORY = []
# 图片黑名单
FREEBUF_PIC_BLACKLIST = [
    ""
]
# ? 先知爬虫设置 -----
# 先知的反爬很恶心，会让你滑动解锁。
# 设置默认开始页
XIANZHI_PAGE_START = 1
# 设置默认结束页面
XIANZHI_PAGE_END = 15070
# 图片黑名单，不让其重复下载浪费时间
XIANZHI_PIC_BLACKLIST = [
    "default_avatar.png",
    '/avatars/'
]
# ? 补天爬虫设置 -----
# butian 分类
# BUTIAN_CATEGORY = ['article', 'share']
BUTIAN_CATEGORY = ['share']
# 设置默认开始页面
BUTIAN_PAGE_START = 1
# 设置默认结束页面
BUTIAN_PAGE_END = 3670

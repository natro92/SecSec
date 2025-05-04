# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 16:08
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : config
# @Project : SecSec


# * 基础设置
# driver路径
DRIVER_PATH = r'chromedriver.exe'
# 文件路径
FILE_SAVE_PATH = r'D:\Workstation\TextWorkSpace\LocalForum'
# 请求头
CRAWLER_HEADERS = [
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
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
# FREEBUF_CATEGORY = ['web']
FREEBUF_CATEGORY = ['vuls', 'web', 'defense']
# 为每个分类单独设置页面范围 {分类: [开始页, 结束页]}
FREEBUF_PAGE_CONFIG = {
    'vuls': [1, 182],
    'web': [1, 150],
    'defense': [1, 100]
}
# 设置默认开始页（兼容旧版）
FREEBUF_PAGE_START = 1
# 设置默认结束页面（兼容旧版）
FREEBUF_PAGE_END = 182
# 图片黑名单
FREEBUF_PIC_BLACKLIST = [
    ""
]
# ? 先知爬虫设置 -----
# 先知的反爬很恶心，会让你滑动解锁。
# 设置默认开始页
# XIANZHI_PAGE_START = 16160
XIANZHI_PAGE_START = 1
# 设置默认结束页面
XIANZHI_PAGE_END = 17853
# 图片黑名单，不让其重复下载浪费时间
XIANZHI_PIC_BLACKLIST = [
    "default_avatar.png",
    '/avatars/'
]
# 设置是否需要 400 错误睡眠
XIANZHI_400_SLEEP = False
# ? 补天爬虫设置 -----
# butian 分类
# BUTIAN_CATEGORY = ['article', 'share']
BUTIAN_CATEGORY = ['share']
# 设置默认开始页面
BUTIAN_PAGE_START = 2118
# 设置默认结束页面
BUTIAN_PAGE_END = 3835

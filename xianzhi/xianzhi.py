#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Project : SecCrawler 
@File    : xianzhi
@desc    : 
@Author  : @Natro92
@Date    : 2024/7/24 下午6:41 
@Blog    : https://natro92.fun
@Contact : natro92@natro92.fun
"""
import random
import sys
import threading
import time
from colorama import init, Fore
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import markdownify
from bs4 import BeautifulSoup
import os
import requests
from tqdm import trange, tqdm

from config import *
from utils.files import is_image_folder_created
from utils.text_builder import filename_filter, beautify_md, split_content


def download_image(img_src, images_path, crawler_headers):
    """
    单个图片下载的函数
    :param img_src: 图片的源地址
    :param images_path: 图片保存路径
    :param crawler_headers: 请求头
    """
    # * 部分先知社区的图床掉了，比如：10315 的部分图片
    if not img_src:
        return
    if any(blacklisted in img_src for blacklisted in XIANZHI_PIC_BLACKLIST):
        # tqdm.write(f'[*] Info - 图片地址在黑名单中，跳过下载 {img_src}')
        return
    if img_src.startswith('/'):
        img_src = 'https://xz.aliyun.com' + img_src
    if not img_src or 'http' not in img_src:
        tqdm.write(Fore.RED + f'[?] Warn - 图片格式错误 {img_src}' + Fore.RESET)
        return
    img_name = os.path.basename(img_src).replace('!small', '').split('?')[0].split('#')[0]
    # * 加个固定Referrer，存储桶有检测
    crawler_headers['Referer'] = "https://xz.aliyun.com/"
    try:
        img_pic = requests.get(img_src, headers=crawler_headers).content
    except Exception as e:
        tqdm.write(Fore.RED + f'[!] Error - 无法下载图片从 {img_src}: {e}' + Fore.RESET)
        return
    with open(os.path.join(images_path, img_name), 'wb') as f:
        f.write(img_pic)


def download_images(img_tags, images_path, crawler_headers, max_threads=THREADS_NUM):
    """
    下载图片的函数（多线程，限制线程数量）
    :param img_tags: 图片标签列表
    :param images_path: 图片保存路径
    :param crawler_headers: 请求头
    :param max_threads: 最大线程数量
    """
    threads = []
    thread_count = 0

    for img_tag in img_tags:
        img_src = img_tag.get("src")
        if thread_count >= max_threads:
            for thread in threads:
                thread.join()
            threads = []
            thread_count = 0

        thread = threading.Thread(target=download_image, args=(img_src, images_path, crawler_headers))
        threads.append(thread)
        thread.start()
        thread_count += 1

    # 确保最后剩余的线程也能完成
    for thread in threads:
        thread.join()


def process_post(driver):
    """
    处理先知文章，这个别改了，越改复杂度越高，黄线太恶心人了。
    :param driver:
    :return:
    """
    base_url = 'https://xz.aliyun.com/t/{post_index}'
    for post_index in trange(XIANZHI_PAGE_START, XIANZHI_PAGE_END + 1, desc='[+] 正在爬取先知社区文章'):
        url = base_url.format(post_index=post_index)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title_tag = soup.find('title')
        # * 判断是否是从验证页面跳转出的
        while '滑动验证页面' in title_tag.text:
            tqdm.write(Fore.YELLOW + f'[?] WARN - 需要滑动验证，等待验证' + Fore.RESET)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            title_tag = soup.find('title')
        post_title = filename_filter(title_tag.text) if title_tag else None
        filename = os.path.join(FILE_SAVE_PATH, 'xianzhi', f'{post_index}-{post_title}.md')
        if not post_title or ('400 -' in post_title):
            tqdm.write(Fore.RED + f'[!] Error - {post_index} 未找到该文章' + Fore.RESET)
            continue
        if os.path.exists(filename):
            tqdm.write(f'[*] Info - {post_index}-{post_title} 已经爬取过，跳过')
            continue
        img_tags = soup.find_all('img')
        is_image_folder_created('xianzhi')
        download_images(img_tags, os.path.join(FILE_SAVE_PATH, 'xianzhi', 'images'), random.choice(CRAWLER_HEADERS))
        md_content = markdownify.markdownify(driver.page_source, heading_style="ATX")
        md_content = process_images(md_content, img_tags)  # 调用新函数处理图片相关操作
        md_content = beautify_md(md_content)
        md_content = md_content.replace('#### 积分打赏\n\n 1分\n \n\n 2分\n \n\n 5分\n \n\n  \n 8分\n \n\n 10分\n \n\n 20分\n \n\n关闭\n确定', '')
        split_strings = ['\n\n[登录]', '\n[**登录**]']
        md_content = split_content(md_content, split_strings)
        save_post(post_index, post_title, md_content, filename)
        actual_sleep_time = SLEEP_TIME + random.uniform(-SLEEP_TIME_DELTA, SLEEP_TIME_DELTA)
        time.sleep(actual_sleep_time)


def process_images(md_content, img_tags):
    """
    处理图片相关的替换操作，不抽出来复杂度太高了，看的迷糊
    :param md_content: 原始的 Markdown 内容
    :param img_tags: 图片标签列表
    :return: 处理后的 Markdown 内容
    """
    for img_tag in img_tags:
        img_src = img_tag.get("src", "images/default_avatar.png")
        img_src = img_src if img_src else None
        if img_src is None:
            continue
        img_name = os.path.basename(img_src).replace('!small', '').split('?')[0].split('#')[0]
        # print(img_src, img_name)
        md_content = md_content.replace(img_src, f'images/{img_name}')
    return md_content


def save_post(post_index, post_title, md_content, filename):
    """
    保存文章
    :param post_index: 文章编号
    :param post_title: 文章标题
    :param md_content: 文章内容
    :param filename: 文件名
    """
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(md_content)
    tqdm.write(Fore.GREEN + f'[*] Info - {str(post_index)}-{post_title} 爬取完成' + Fore.RESET)


def run_xianzhi_crawler():
    """
    运行先知爬虫
    :return:
    """
    init(autoreset=True)
    chrome_options = webdriver.ChromeOptions()
    # ! 一行配置绕过阿里云机器人验证手动失效，webdriver和普通浏览器参数不同。
    # https://blog.csdn.net/weixin_45081575/article/details/126585575
    chrome_options.add_argument("disable-blink-features=AutomationControlled")
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=chrome_options)

    if not XIANZHI_PAGE_START or not XIANZHI_PAGE_END:
        tqdm.write(f'{Fore.RED}[!] Error - 请先在config.py中设置开始页和结束页')
        exit(1)

    process_post(driver)
    driver.quit()

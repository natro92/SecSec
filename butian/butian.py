#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Project : SecCrawler 
@File    : butian
@desc    : 
@Author  : @Natro92
@Date    : 2024/7/25 下午7:44 
@Blog    : https://natro92.fun
@Contact : natro92@natro92.fun
"""
import ast
import random
import re
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
    # if img_src.startswith('/'):
    #     img_src = 'https://www.freebuf.com' + img_src
    # if img_src.startswith('/images/'):
    #     img_src = 'https://image.3001.net' + img_src
    if not img_src:
        return
    if 'http' not in img_src:
        tqdm.write(Fore.YELLOW + f'[?] Warn - 图片格式错误 {img_src}' + Fore.RESET)
        return
    img_name = os.path.basename(img_src).replace('!small', '').split('?')[0]
    if not img_name:
        tqdm.write(Fore.YELLOW + f'[?] Warn - 图片名称为空 {img_src}' + Fore.RESET)
        return
    try:
        img_pic = requests.get(img_src, headers=crawler_headers).content
    except Exception as e:
        tqdm.write(Fore.RED + f'[!] Error - 无法下载图片从 {img_src}: {e}' + Fore.RESET)
        return
    with open(os.path.join(images_path, img_name), 'wb') as f:
        f.write(img_pic)


def download_images(img_tags, images_path, crawler_headers, max_threads=THREADS_NUM):
    """
    下载图片的函数
    :param max_threads:
    :param img_tags: 图片标签列表
    :param images_path: 图片保存路径
    :param crawler_headers: 请求头
    """
    threads = []
    thread_count = 0  # 用于跟踪当前线程数量

    for img_tag in img_tags:
        img_src = img_tag.get("src", 'images/default_avatar.jpg')
        if thread_count >= max_threads:
            for thread in threads:
                thread.join()
            threads = []
            thread_count = 0

        thread = threading.Thread(target=download_image, args=(img_src, images_path, crawler_headers))
        threads.append(thread)
        thread.start()
        thread_count += 1

    for thread in threads:
        thread.join()


def save_post(post_index, post_title, md_content, file_path):
    """
    保存文章内容到文件
    :param post_index: 文章索引
    :param post_title: 文章标题
    :param md_content: 文章内容
    :param file_path: 文件保存路径
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    tqdm.write(Fore.GREEN + f'[*] Info - {post_index}-{post_title} 爬取完成')


def process_post(driver):
    """
    处理单个文章
    :param driver: 浏览器驱动
    """
    base_url = r'https://forum.butian.net/{category}/{post_index}'
    is_image_folder_created('butian')
    for category in BUTIAN_CATEGORY:
        for post_index in trange(BUTIAN_PAGE_START, BUTIAN_PAGE_END, desc='[+] 正在爬取 Butian 文章'):
            url = base_url.format(category=category, post_index=post_index)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            title_tag = soup.find('title')
            post_title = filename_filter(title_tag.text) if title_tag else None
            if not post_title or ('404' in post_title):
                tqdm.write(Fore.RED + f'[!] Error - {post_index} 未找到该文章' + Fore.RESET)
                continue
            post_title = post_title[8:]
            filename = os.path.join(FILE_SAVE_PATH, 'butian', f'{post_index}-{post_title}.md')
            if os.path.exists(filename):
                tqdm.write(f'[*] Info - {post_index}-{post_title} 已经爬取过，跳过')
                continue
            img_tags = soup.find_all('img')
            download_images(img_tags, os.path.join(FILE_SAVE_PATH, 'butian', 'images'), random.choice(CRAWLER_HEADERS))
            md_content = markdownify.markdownify(driver.page_source)
            split_strings = [check_split_strings(md_content, post_title), '* 发表于 ']
            md_content = split_content(md_content, split_strings)
            md_content = process_images(md_content, img_tags)  # 调用新函数处理图片相关操作
            md_content = beautify_md(md_content)
            save_post(post_index, post_title, md_content, filename)
            actual_sleep_time = SLEEP_TIME + random.uniform(-SLEEP_TIME_DELTA, SLEEP_TIME_DELTA)
            time.sleep(actual_sleep_time)


def check_split_strings(md_content, post_title):
    if len(post_title) * '=' in md_content:
        return len(post_title) * '='
    else:
        return len(post_title) * '-'


def process_images(md_content, img_tags):
    """
    处理图片相关的替换操作，不抽出来复杂度太高了，看的迷糊
    :param md_content: 原始的 Markdown 内容
    :param img_tags: 图片标签列表
    :return: 处理后的 Markdown 内容
    """
    for img_tag in img_tags:
        img_src = img_tag.get("src", "images/freebuf-头像.jpg")
        img_src = img_src if img_src else None
        if img_src is None:
            continue
        img_name = os.path.basename(img_src).replace('!small', '').split('?')[0].split('#')[0]
        # print(img_src, img_name)
        md_content = md_content.replace(img_src, f'images/{img_name}')
    return md_content


def process_post_reload(category, post_index, post_title, driver):
    """
    重新下载某一篇文章
    :param category: 分类
    :param post_index: index
    :param post_title: 标题
    :param driver: 驱动
    :return:
    """
    base_url = r'https://www.freebuf.com/articles/{category}/{post_index}.html'
    filename = os.path.join(FILE_SAVE_PATH, 'freebuf',
                            post_index + "-" + filename_filter(post_title) + '.md')
    post_url = base_url.format(category=category, post_index=post_index)
    driver.get(post_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    img_tags = soup.find_all('img')
    if not os.path.exists(os.path.join(FILE_SAVE_PATH, 'freebuf', 'images')):
        os.makedirs(os.path.join(FILE_SAVE_PATH, 'freebuf', 'images'))
    download_images(img_tags, os.path.join(FILE_SAVE_PATH, 'freebuf', 'images'),
                    random.choice(CRAWLER_HEADERS))
    md_content = markdownify.markdownify(driver.page_source, heading_style="ATX")
    md_content = process_images_reload(md_content, img_tags)  # 调用新函数处理图片相关操作
    # * 专属美化 Markdown
    md_content = beautify_md(md_content)
    split_strings = ['官方公众号企业安全新浪微博',
                     '未经允许不得转载，授权请联系FreeBuf客服小蜜蜂，微信：freebee2022']
    md_content = split_content(md_content, split_strings)
    save_post(post_index, post_title, md_content, filename)


def process_images_reload(md_content, img_tags):
    """
    重新下载图片
    :param md_content: Markdown内容
    :param img_tags: 图片标签列表
    :return: 处理后的 Markdown 内容
    """
    for img_tag in img_tags:
        img_src = img_tag.get("src", "images/freebuf-头像.jpg")
        img_src = img_src if img_src else None
        if img_src is None:
            continue
        img_name = os.path.basename(img_src).replace('!small', '').split('?')[0].split('#')[0]
        md_content = md_content.replace(img_src, f'images/{img_name}')
    return md_content


def run_butian_crawler():
    """
    运行 butian 爬虫
    :return:
    """
    init(autoreset=True)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("disable-blink-features=AutomationControlled")
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=chrome_options)

    if not BUTIAN_CATEGORY:
        tqdm.write(Fore.RED + '[!] Error - 未配置 Butian 分类，请检查 config.py 文件')
        exit(1)
    if not BUTIAN_PAGE_START or not BUTIAN_PAGE_END:
        tqdm.write(Fore.RED + '[!] Error - 未配置 Butian 初始页数，请检查 config.py 文件')
        exit(1)

    process_post(driver)

    driver.quit()

# def run_freebuf_crawler_by_id(lines):
#     """
#     运行 FreeBuf 爬虫根据id进行文件下载
#     :param lines: redownload.txt文件内容
#     :return:
#     """
#     init(autoreset=True)
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument("disable-blink-features=AutomationControlled")
#     chrome_options.add_argument('--ignore-certificate-errors')
#     driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=chrome_options)
#     for line in tqdm(lines):
#         line = line.strip()
#         category = line.split('||')[0]
#         filename_ex = line.split('||')[1]
#         file_id = filename_ex.split('-')[0]
#         filename_real = filename_ex[7:-3]
#         # print(category, filename_ex, file_id)
#         # filename = os.path.join(FILE_SAVE_PATH, 'freebuf', filename_ex)
#         tqdm.write(f'[*] Info - 正在重新爬取 {filename_ex[:-3]}')
#         # if os.path.exists(filename):
#         #     # 使用重新爬取
#         #     tqdm.write(f'[*] Info - 正在重新爬取 {filename_ex[:-3]}')
#         #     run_freebuf_crawler_by_id(category, int(file_id))
#         # else:
#         #     tqdm.write(Fore.YELLOW + f'[?] Wrong - {line} 该文件不存在' + Fore.RESET)
#         #     continue
#         process_post_reload(category, file_id, filename_real, driver)

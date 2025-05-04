# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 23:34
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : crawler_run
# @Project : SecSec

import os
import random
import re
import threading
import time

import markdownify
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from tqdm import tqdm, trange

from config import *
from src.Crawler.Base.crawler_init import init_local_chrome
from src.Utils.file_manager import ensure_directory_exists, is_image_folder_created
from src.Utils.log_manager import fail
from src.Utils.text_builder import filename_filter


def run_butian_crawler():
    """
    运行 Butian 爬虫
    :return:
    """
    driver_local = init_local_chrome()

    if not BUTIAN_CATEGORY:
        tqdm.write(fail("[!] Error - 未配置 Butian 分类，请检查 config.py 文件"))
        exit(1)
    if not BUTIAN_PAGE_START or not BUTIAN_PAGE_END:
        tqdm.write(fail("[!] Error - 未配置 Butian 初始页数，请检查 config.py 文件"))
        exit(1)

    butian_crawler_main(driver_local)
    driver_local.quit()


def butian_crawler_main(driver):
    """
    处理 Butian 文章
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
            # md_content = split_content(md_content, split_strings)
            md_content = process_images(md_content, img_tags)
            # md_content = beautify_md(md_content)
            save_post(post_index, post_title, md_content, filename)

            actual_sleep_time = SLEEP_TIME + random.uniform(-SLEEP_TIME_DELTA, SLEEP_TIME_DELTA)
            time.sleep(actual_sleep_time)


def check_split_strings(md_content, post_title):
    """
    检查分割字符串
    :param md_content: Markdown内容
    :param post_title: 文章标题
    :return: 分割字符串
    """
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
        img_src = img_tag.get("src", "images/default_avatar.jpg")
        img_src = img_src if img_src else None
        if img_src is None:
            continue
        img_name = os.path.basename(img_src).replace('!small', '').split('?')[0].split('#')[0]
        md_content = md_content.replace(img_src, f'images/{img_name}')
    return md_content


def save_post(post_index, post_title, md_content, filename):
    """
    保存文章内容到文件
    :param post_index: 文章索引
    :param post_title: 文章标题
    :param md_content: 文章内容
    :param filename: 文件保存路径
    """
    ensure_directory_exists(filename)
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(md_content)
    tqdm.write(Fore.GREEN + f'[*] Info - {post_index}-{post_title} 爬取完成' + Fore.RESET)


def download_images(img_tags, images_path, crawler_headers, max_threads=THREADS_NUM):
    """
    下载图片的函数（多线程，限制线程数量）
    :param img_tags: 图片标签列表
    :param images_path: 图片保存路径
    :param crawler_headers: 请求头
    :param max_threads: 最大线程数量
    """
    session = requests.Session()
    session.headers.update(crawler_headers)

    for img_tag in img_tags:
        img_src = img_tag.get("src", 'images/default_avatar.jpg')
        # 创建一个线程来下载图片
        thread = threading.Thread(target=download_image_with_session, args=(img_src, images_path, session))
        thread.start()


def download_image_with_session(img_src, images_path, session):
    """
    使用session的单个图片下载函数
    :param img_src: 图片的源地址
    :param images_path: 图片保存路径
    :param session: requests.Session 对象
    """
    if not img_src:
        return
    if 'http' not in img_src:
        tqdm.write(Fore.YELLOW + f'[?] Warn - 图片格式错误 {img_src}' + Fore.RESET)
        return
    img_name = os.path.basename(img_src).replace('!small', '').split('?')[0]
    if not img_name:
        tqdm.write(Fore.YELLOW + f'[?] Warn - 图片名称为空 {img_src}' + Fore.RESET)
        return
    image_path = os.path.join(images_path, img_name)
    if os.path.exists(image_path):
        return
    try:
        img_pic = session.get(img_src, timeout=10).content  # 添加超时时间
        with open(image_path, 'wb') as f:
            f.write(img_pic)
    except Exception as e:
        tqdm.write(Fore.RED + f'[!] Error - 无法下载图片从 {img_src}: {e}' + Fore.RESET)
        return


def process_post_reload(category, post_index, post_title, driver):
    """
    重新下载某一篇文章
    :param category: 分类
    :param post_index: index
    :param post_title: 标题
    :param driver: 驱动
    :return:
    """
    base_url = r'https://forum.butian.net/{category}/{post_index}'
    filename = os.path.join(FILE_SAVE_PATH, 'butian',
                            f"{post_index}-{filename_filter(post_title)}.md")
    post_url = base_url.format(category=category, post_index=post_index)
    driver.get(post_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    img_tags = soup.find_all('img')
    is_image_folder_created('butian')
    download_images(img_tags, os.path.join(FILE_SAVE_PATH, 'butian', 'images'),
                    random.choice(CRAWLER_HEADERS))
    md_content = markdownify.markdownify(driver.page_source)
    split_strings = [check_split_strings(md_content, post_title), '* 发表于 ']
    md_content = split_content(md_content, split_strings)
    md_content = process_images(md_content, img_tags)
    md_content = beautify_md(md_content)
    save_post(post_index, post_title, md_content, filename)

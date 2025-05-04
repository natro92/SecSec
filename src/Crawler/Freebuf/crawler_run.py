# _*_ coding : utf-8 _*_
# @Time: 2024/7/25 19:44
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : crawler_run
# @Project : SecSec

import os
import random
import re
import sys
import threading
import time

import markdownify
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from tqdm import tqdm, trange

from config import *
from src.Crawler.Base.crawler_init import init_local_chrome
from src.Utils.file_manager import ensure_directory_exists, is_image_folder_created
from src.Utils.log_manager import fail
from src.Utils.text_builder import filename_filter


def run_freebuf_crawler():
    """
    运行 FreeBuf 爬虫
    """
    driver_local = init_local_chrome()
    if not FREEBUF_CATEGORY:
        tqdm.write(fail("[!] Error - 未配置 FreeBuf 分类，请检查 config.py 文件"))
        exit(1)

    # 检查是否使用新的分页配置
    use_new_config = hasattr(sys.modules['config'], 'FREEBUF_PAGE_CONFIG')

    # 如果没有新配置，检查旧配置是否存在
    if not use_new_config and (not FREEBUF_PAGE_START or not FREEBUF_PAGE_END):
        tqdm.write(fail("[!] Error - 未配置 FreeBuf 初始页数，请检查 config.py 文件"))
        exit(1)

    freebuf_crawler_main(driver_local, use_new_config)
    driver_local.quit()


def freebuf_crawler_main(driver, use_new_config):
    """
    处理FreeBuf文章的主函数
    :param driver: 浏览器驱动
    :param use_new_config: 是否使用新的分页配置
    """
    for category in FREEBUF_CATEGORY:
        # 确定当前分类的开始页和结束页
        if use_new_config and category in FREEBUF_PAGE_CONFIG:
            start_page = FREEBUF_PAGE_CONFIG[category][0]
            end_page = FREEBUF_PAGE_CONFIG[category][1]
        else:
            # 使用默认配置
            start_page = FREEBUF_PAGE_START
            end_page = FREEBUF_PAGE_END

        tqdm.write(f'[*] Info - 开始爬取 FreeBuf {category} 分类，页面范围: {start_page}-{end_page}')

        for category_page in trange(start_page, end_page + 1, desc=f'[+] 正在爬取 Freebuf {category} 文章'):
            page_json = get_page_data(category, category_page)
            if not page_json or not page_json['data']['data_list']:
                tqdm.write(Fore.GREEN + f'[*] Info - FreeBuf {category} 分类爬取完成')
                break
            for post in page_json['data']['data_list']:
                process_post(category, post, driver)
            actual_sleep_time = SLEEP_TIME + random.uniform(-SLEEP_TIME_DELTA, SLEEP_TIME_DELTA)
            time.sleep(actual_sleep_time)


def get_page_data(category, category_page):
    """
    获取页面数据
    :param category: 分类
    :param category_page: 页码
    :return: 页面的 JSON 数据
    """
    page_base_url = r'https://www.freebuf.com/fapi/frontend/category/list?name={category}&tag=category&limit=20&page={category_page}&select=0&order=0'
    try:
        tqdm.write(f'[*] Info - 正在爬取 FreeBuf {category} 分类第 {category_page} 页')
        page_url = page_base_url.format(category=category, category_page=category_page)
        page_json = requests.get(page_url, headers=random.choice(CRAWLER_HEADERS), timeout=5).json()
        return page_json
    except requests.exceptions.Timeout as e:
        tqdm.write(Fore.RED + f'[!] Error - 请求超时: {e}' + Fore.RESET)
    except requests.exceptions.RequestException as e:
        tqdm.write(Fore.RED + f'[!] Error - 请求出错: {e}' + Fore.RESET)


def process_post(category, post, driver):
    """
    处理单个文章
    :param category: 分类
    :param post: 文章数据
    :param driver: 浏览器驱动
    """
    base_url = r'https://www.freebuf.com/articles/{category}/{post_index}.html'

    post_index = post['ID']
    post_title = post['post_title']
    post_is_paid = post['paid_read']
    filename = os.path.join(FILE_SAVE_PATH, 'freebuf',
                            post_index + "-" + filename_filter(post_title) + '.md')

    if post_is_paid:
        tqdm.write(f'[*] Info - {post_index}-{post_title} 为付费文章，跳过')
        return

    if os.path.exists(filename):
        tqdm.write(f'[*] Info - {post_index}-{post_title} 已经爬取过，跳过')
        return

    post_url = base_url.format(category=category, post_index=post_index)
    driver.get(post_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    img_tags = soup.find_all('img')
    is_image_folder_created('freebuf')
    download_images(img_tags, os.path.join(FILE_SAVE_PATH, 'freebuf', 'images'),
                    random.choice(CRAWLER_HEADERS))

    md_content = markdownify.markdownify(driver.page_source, heading_style="ATX")
    md_content = process_images(md_content, img_tags)
    md_content = cut_md(md_content)
    save_post(post_index, post_title, md_content, filename)


def cut_md(md_content):
    content = ''
    # ! 前段
    match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", md_content)
    if match:
        parts = re.split(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", md_content)
        content = parts[1]
    else:
        content = md_content

    # ! 后段
    match = re.search(r"如需授权、对文章有疑问或需删除稿件，请联系 FreeBuf 客服小蜜蜂（微信：freebee1024）", content)
    if match:
        parts = re.split(r"如需授权、对文章有疑问或需删除稿件，请联系 FreeBuf 客服小蜜蜂（微信：freebee1024）", content)
        content = parts[0]
    else:
        content = content

    return content


def process_images(md_content, img_tags):
    """
    处理图片相关的替换操作
    :param md_content: 原始的 Markdown 内容
    :param img_tags: 图片标签列表
    :return: 处理后的 Markdown 内容
    """
    for img_tag in img_tags:
        img_src = img_tag.get("src", "images/freebuf-头像.jpg")
        if not img_src:
            continue
        img_name = os.path.basename(img_src).replace('!small', '').split('?')[0].split('#')[0]
        md_content = md_content.replace(img_src, f'images/{img_name}')
    return md_content


def download_images(img_tags, images_path, crawler_headers, max_threads=THREADS_NUM):
    """
    下载图片的函数
    :param img_tags: 图片标签列表
    :param images_path: 图片保存路径
    :param crawler_headers: 请求头
    :param max_threads: 最大线程数量
    """
    session = requests.Session()
    session.headers.update(crawler_headers)

    for img_tag in img_tags:
        img_src = img_tag.get("src", '/images/20210324/1616566754_605ad9e27112e9d374174.png')
        # 创建一个线程来下载图片
        thread = threading.Thread(target=download_image_with_session,
                                  args=(img_src, images_path, session))
        thread.start()


def download_image_with_session(img_src, images_path, session):
    """
    使用session的单个图片下载函数
    :param img_src: 图片的源地址
    :param images_path: 图片保存路径
    :param session: requests.Session 对象
    """
    # 处理相对路径
    if img_src.startswith('/'):
        img_src = 'https://www.freebuf.com' + img_src
    if img_src.startswith('/images/'):
        img_src = 'https://image.3001.net' + img_src

    # 验证URL格式
    if not img_src or 'http' not in img_src:
        # tqdm.write(Fore.YELLOW + f'[?] Warn - 图片格式错误 {img_src}' + Fore.RESET)
        return

    # 提取文件名
    img_name = os.path.basename(img_src).replace('!small', '').split('?')[0]
    if not img_name:
        # tqdm.write(Fore.YELLOW + f'[?] Warn - 图片名称为空 {img_src}' + Fore.RESET)
        return

    # 检查文件是否已存在
    image_path = os.path.join(images_path, img_name)
    if os.path.exists(image_path):
        return

    # 下载图片
    try:
        img_pic = session.get(img_src, timeout=10).content
        with open(image_path, 'wb') as f:
            f.write(img_pic)
    except Exception as e:
        tqdm.write(Fore.RED + f'[!] Error - 无法下载图片从 {img_src}: {e}' + Fore.RESET)
        return


def save_post(post_index, post_title, md_content, filename):
    """
    保存文章
    :param post_index: 文章编号
    :param post_title: 文章标题
    :param md_content: 文章内容
    :param filename: 文件名
    """
    ensure_directory_exists(filename)
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(md_content)
    tqdm.write(Fore.GREEN + f'[*] Info - {post_index}-{post_title} 爬取完成' + Fore.RESET)


def run_freebuf_crawler_by_id(lines):
    """
    根据ID运行FreeBuf爬虫
    :param lines: redownload.txt文件内容
    """
    driver_local = init_local_chrome()

    for line in tqdm(lines):
        line = line.strip()
        category = line.split('||')[0]
        filename_ex = line.split('||')[1]
        file_id = filename_ex.split('-')[0]
        filename_real = filename_ex[7:-3]

        tqdm.write(f'[*] Info - 正在重新爬取 {filename_ex[:-3]}')
        process_post_reload(category, file_id, filename_real, driver_local)

    driver_local.quit()


def process_post_reload(category, post_index, post_title, driver):
    """
    重新下载某一篇文章
    :param category: 分类
    :param post_index: 文章ID
    :param post_title: 文章标题
    :param driver: 驱动
    """
    base_url = r'https://www.freebuf.com/articles/{category}/{post_index}.html'

    filename = os.path.join(FILE_SAVE_PATH, 'freebuf',
                            post_index + "-" + filename_filter(post_title) + '.md')
    post_url = base_url.format(category=category, post_index=post_index)
    driver.get(post_url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    img_tags = soup.find_all('img')
    is_image_folder_created('freebuf')

    download_images(img_tags, os.path.join(FILE_SAVE_PATH, 'freebuf', 'images'),
                    random.choice(CRAWLER_HEADERS))

    md_content = markdownify.markdownify(driver.page_source, heading_style="ATX")
    md_content = process_images(md_content, img_tags)
    # md_content = beautify_md(md_content)

    split_strings = ['官方公众号企业安全新浪微博',
                     '未经允许不得转载，授权请联系FreeBuf客服小蜜蜂，微信：freebee2022']
    # md_content = split_content(md_content, split_strings)

    save_post(post_index, post_title, md_content, filename)

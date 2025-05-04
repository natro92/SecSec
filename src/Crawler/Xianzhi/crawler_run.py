# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 17:11
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
from telnetlib import EC
from urllib.parse import urlparse
import socket
import requests.exceptions

import markdownify
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm, trange

from config import *
from src.Crawler.Base.crawler_init import init_local_chrome
from src.Utils.file_manager import ensure_directory_exists, is_image_folder_created
from src.Utils.log_manager import fail
from src.Utils.text_builder import filename_filter


def run_xianzhi_crawler():
    """
    运行Xianzhi爬虫
    :return:
    """
    driver_local = init_local_chrome()
    if not XIANZHI_PAGE_START or not XIANZHI_PAGE_END:
        tqdm.write(fail("[!] Error - 请先在config.py中设置开始页和结束页"))
        exit(1)
    xianzhi_crawler_main(driver_local)
    driver_local.quit()


def xianzhi_crawler_main(driver):
    """
    处理先知文章，这个别改了，越改复杂度越高，黄线太恶心人了。
    :param driver:
    :return:
    """
    base_url = 'https://xz.aliyun.com/news/{post_index}'
    cached_title = None  # 缓存上一篇文章的标题

    for post_index in trange(XIANZHI_PAGE_START, XIANZHI_PAGE_END + 1, desc='[+] 正在爬取先知社区文章'):
        url = base_url.format(post_index=post_index)
        driver.get(url)
        try:
            # 确保内容不为空
            WebDriverWait(driver, 3).until(
                lambda d: len(d.find_element(By.CSS_SELECTOR, "#markdown-body").text.strip()) > 0
            )
        except TimeoutException:
            tqdm.write(Fore.YELLOW + f'[?] WARN - 页面 {post_index} 加载超时' + Fore.RESET)
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title_tag = soup.find('title')
        title_tag = title_tag if title_tag else soup.find('h1')
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
            if XIANZHI_400_SLEEP:
                actual_sleep_time = SLEEP_TIME + random.uniform(-SLEEP_TIME_DELTA, SLEEP_TIME_DELTA)
                time.sleep(actual_sleep_time)
            continue

        # 检查当前文章标题是否与缓存标题相同
        if cached_title and post_title == cached_title:
            tqdm.write(Fore.YELLOW + f'[?] WARN - {post_index}-{post_title} 标题与上一篇相同，跳过' + Fore.RESET)
            continue

        # 更新缓存标题
        cached_title = post_title

        if os.path.exists(filename):
            tqdm.write(f'[*] Info - {post_index}-{post_title} 已经爬取过，跳过')
            continue
        img_tags = soup.find_all('img')
        is_image_folder_created('xianzhi')
        download_images(img_tags, os.path.join(FILE_SAVE_PATH, 'xianzhi', 'images'), random.choice(CRAWLER_HEADERS))
        md_content = markdownify.markdownify(driver.page_source, heading_style="ATX")
        if "请查看其他资讯" in md_content:
            # 发现“请查看其他资讯”，直接跳过
            tqdm.write(Fore.YELLOW + f'[?] WARN - 页面 {post_index} 显示“请查看其他资讯”，跳过' + Fore.RESET)
            if XIANZHI_400_SLEEP:
                actual_sleep_time = SLEEP_TIME + random.uniform(-SLEEP_TIME_DELTA, SLEEP_TIME_DELTA)
                time.sleep(actual_sleep_time)
            continue
        md_content = process_images(md_content, img_tags)  # 调用新函数处理图片相关操作
        md_content = cut_md(md_content)
        save_post(post_index, post_title, md_content, filename)
        continue  # 保存文章后立即跳到下一篇文章
        actual_sleep_time = SLEEP_TIME + random.uniform(-SLEEP_TIME_DELTA, SLEEP_TIME_DELTA)
        time.sleep(actual_sleep_time)


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
    tqdm.write(Fore.GREEN + f'[*] Info - {str(post_index)}-{post_title} 爬取完成' + Fore.RESET)


def cut_md(md_content):
    content = ''
    # ! 前段
    match = re.search(r"浏览 · ", md_content)
    if match:
        parts = re.split(r"浏览 · ", md_content)
        content = parts[1]
    else:
        content = md_content

    # ! 后段
    match = re.search(r"\[(\d+) 人收藏\]", content)
    if match:
        parts = re.split(r"\[(\d+) 人收藏\]", content)
        content = parts[0]
    else:
        content = content

    return content


def tidy_md(md_content):
    """
    清理Markdown内容
    :param md_content:
    :return:
    """
    # 处理图片
    soup = BeautifulSoup(md_content, 'html.parser')
    for img in soup.find_all('img'):
        img['style'] = 'max-width: 100%; height: auto;'
        img['class'] = 'img-responsive'
        img['alt'] = 'image'
        img['title'] = 'image'
    return str(soup)


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


def is_valid_remote_url(url):
    """
    验证URL是否为有效的远程地址
    """
    try:
        parsed = urlparse(url)
        # 检查是否为本地地址
        if parsed.hostname in ('localhost', '127.0.0.1') or \
                parsed.hostname.startswith(('192.168.', '10.', '172.')):
            return False

        # 检查端口
        if parsed.port == 7541:  # 已知问题端口
            return False

        # 验证域名是否可解析
        if parsed.hostname:
            socket.gethostbyname(parsed.hostname)

        return all([parsed.scheme in ('http', 'https'), parsed.netloc])
    except (socket.gaierror, ValueError, AttributeError):
        return False


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
    image_path = os.path.join(images_path, img_name)
    if os.path.exists(image_path):
        # tqdm.write(f'[*] Info - 图片已存在，跳过下载 {img_name}')
        return
    # * 加个固定Referrer，存储桶有检测
    crawler_headers['Referer'] = "https://xz.aliyun.com/"
    try:
        img_pic = requests.get(img_src, headers=crawler_headers).content
    except Exception as e:
        tqdm.write(Fore.RED + f'[!] Error - 无法下载图片从 {img_src}: {e}' + Fore.RESET)
        return
    with open(image_path, 'wb') as f:
        f.write(img_pic)


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
        img_src = img_tag.get("src")
        # 创建一个线程来下载图片
        thread = threading.Thread(target=download_image_with_session, args=(img_src, images_path, session))
        thread.start()


def download_image_with_session(img_src, images_path, session):
    """
    使用session的单个图片下载函数，增强错误处理
    """
    try:
        # 基本检查
        if not img_src:
            return

        # 黑名单检查
        if any(blacklisted in img_src for blacklisted in XIANZHI_PIC_BLACKLIST):
            return

        # 处理相对路径
        if img_src.startswith('/'):
            img_src = 'https://xz.aliyun.com' + img_src

        # URL格式验证
        if not is_valid_remote_url(img_src):
            tqdm.write(Fore.YELLOW + f'[?] Warn - 无效的图片URL: {img_src}' + Fore.RESET)
            return

        img_name = os.path.basename(img_src).replace('!small', '').split('?')[0].split('#')[0]
        image_path = os.path.join(images_path, img_name)

        if os.path.exists(image_path):
            return

        # 设置请求头和参数
        headers = {
            'Referer': 'https://xz.aliyun.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'User-Agent': session.headers.get('User-Agent'),
        }

        # 发送请求
        response = session.get(
            img_src,
            headers=headers,
            timeout=(5, 15),  # (连接超时, 读取超时)
            verify=False,  # 忽略SSL证书验证
            allow_redirects=True
        )

        # 检查响应
        if response.status_code != 200:
            tqdm.write(Fore.YELLOW + f'[?] Warn - 图片下载失败 {img_src}, 状态码: {response.status_code}' + Fore.RESET)
            return

        # 验证内容类型
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            tqdm.write(Fore.YELLOW + f'[?] Warn - 非图片类型响应: {img_src}, 类型: {content_type}' + Fore.RESET)
            return

        # 保存图片
        with open(image_path, 'wb') as f:
            f.write(response.content)

    except requests.exceptions.Timeout:
        tqdm.write(Fore.RED + f'[!] Error - 下载图片超时: {img_src}' + Fore.RESET)
    except requests.exceptions.ConnectionError:
        tqdm.write(Fore.RED + f'[!] Error - 连接错误: {img_src}' + Fore.RESET)
    except requests.exceptions.RequestException as e:
        tqdm.write(Fore.RED + f'[!] Error - 请求异常: {img_src}, 错误: {str(e)}' + Fore.RESET)
    except Exception as e:
        tqdm.write(Fore.RED + f'[!] Error - 未知错误: {img_src}, 错误: {str(e)}' + Fore.RESET)

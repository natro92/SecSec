#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Project : SecCrawler 
@File    : freebuf_ex
@desc    : 
@Author  : @Natro92
@Date    : 2024/7/25 下午8:06 
@Blog    : https://natro92.fun
@Contact : natro92@natro92.fun
"""
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Project : SecCrawler 
@File    : freebuf
@desc    : 
@Author  : @Natro92
@Date    : 2024/7/25 上午1:12 
@Blog    : https://natro92.fun
@Contact : natro92@natro92.fun
"""
import random
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import markdownify
from bs4 import BeautifulSoup
import os
import requests

from config import *
from utils.text_builder import filename_filter, beautify_md


def run_freebuf_crawler():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(service=Service(os.path.join(DRIVER_PATH)), options=chrome_options)

    base_url = r'https://www.freebuf.com/articles/{category}/{post_index}.html'
    page_base_url = r'https://www.freebuf.com/fapi/frontend/category/list?name={category}&tag=category&limit=20&page={category_page}&select=0&order=0'
    next_category = False

    if not FREEBUF_CATEGORY:
        print('[*] Error - 未配置 FreeBuf 分类，请检查 config.py 文件')
        exit(1)
    if not FREEBUF_PAGE_START:
        print('[*] Error - 未配置 FreeBuf 初始页数，请检查 config.py 文件')
        exit(1)
    for category in FREEBUF_CATEGORY:
        # 29
        for category_page in range(FREEBUF_PAGE_START, 888):
            try:
                print(f'[*] Info - 正在爬取 FreeBuf {category} 分类第 {category_page} 页')
                page_url = page_base_url.format(category=category, category_page=category_page)
                page_json = requests.get(page_url, headers=random.choice(CRAWLER_HEADERS), timeout=5).json()
                if not page_json['data']['data_list']:
                    print(f'[*] Info - FreeBuf {category} 分类爬取完成')
                    break
                print(f'[*] Info - 成功获取 FreeBuf {category} 分类第 {category_page} 页信息')
                for post in page_json['data']['data_list']:
                    post_index = post['ID']
                    post_title = post['post_title']
                    post_is_paid = post['paid_read']
                    filename = os.path.join(FILE_SAVE_PATH, 'freebuf', post_index + "-" + filename_filter(post_title) + '.md')
                    if post_is_paid:
                        print(f'[*] Info - {post_index}-{post_title} 为付费文章，跳过')
                        continue
                    if os.path.exists(filename):
                        print(f'[*] Info - {post_index}-{post_title} 已经爬取过，跳过')
                        continue
                    post_url = base_url.format(category=category, post_index=post_index)
                    driver.get(post_url)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    img_tags = soup.find_all('img')
                    if not os.path.exists(os.path.join(FILE_SAVE_PATH, 'freebuf', 'images')):
                        os.makedirs(os.path.join(FILE_SAVE_PATH, 'freebuf', 'images'))
                    for img_tag in img_tags:
                        img_src = img_tag.get("src")
                        if img_src.startswith('/'):
                            img_src = 'https://freebuf.com' + img_src
                        if not img_src or 'http' not in img_src:
                            continue
                        img_name = os.path.basename(img_src).replace('!small', '').split('?')[0]
                        try:
                            img_pic = requests.get(img_src, headers=random.choice(CRAWLER_HEADERS)).content
                        except Exception as e:
                            print(f'[*] Error - Failed to download image from {img_src}: {e}')
                            continue
                        with open(os.path.join(FILE_SAVE_PATH, 'freebuf', 'images', img_name), 'wb') as f:
                            f.write(img_pic)
                    md_content = markdownify.markdownify(driver.page_source, heading_style="ATX")
                    for img_tag in img_tags:
                        img_src = img_tag.get("src")
                        img_name = os.path.basename(img_src).replace('!small', '').split('?')[0]
                        md_content_pre = md_content.replace(img_src, f'images/{img_name}')
                    # * 专属美化 Markdown
                    md_content = beautify_md(md_content_pre)
                    split_strings = ['官方公众号企业安全新浪微博',
                                     '未经允许不得转载，授权请联系FreeBuf客服小蜜蜂，微信：freebee2022']
                    try:
                        if all(s in md_content for s in split_strings):
                            md_content = md_content.split(split_strings[0])[1].split(split_strings[1])[0]
                        else:
                            try:
                                md_content = md_content.split(split_strings[0])[1]
                            except IndexError:
                                print(f'[*] Warning - 第一次切割 {post_index}-{post_title} 失败，重新尝试')
                                try:
                                    md_content = md_content.split(split_strings[1])[0]
                                except IndexError:
                                    print(f'[*] Warning - 第二次切割 {post_index}-{post_title} 失败')
                    except Exception as e:
                        print(f'[*] Error - 文本切割时发生未知错误: {e}')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    print(f'[*] Info - {post_index}-{post_title} 爬取完成')
                if next_category:
                    break
            except Exception as e:
                # * 如果出现
                print(f'[*] Error - {e}')
            time.sleep(10)
    driver.quit()

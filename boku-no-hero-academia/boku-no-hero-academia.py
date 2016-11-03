import requests
from lxml import html
import shutil
import time
import os
import logging
import re
import random
logging.basicConfig(filename='results_hero_academia.log')

domain = "http://eatmanga.com"

def main():
    print("> in main")
    outputPath = "./output/"
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    chapter_manifest_URL = 'http://eatmanga.com/Manga-Scan/Boku-No-Hero-Academia/'
    response = throttled_get_request(chapter_manifest_URL)
    content = html.fromstring(response.content)
    chapters_list =  content.xpath('//table[@id="updates"]/tr/th/a/@href')

    while len(chapters_list) != 0:
        next_page = chapters_list.pop()
        next_url = domain + next_page
        download_chapter(next_url)
        print(next_page + " Remaining: " + str(len(chapters_list)))
    print("< out main")

def download_chapter(url):
    match = re.match(".+\/upcoming\/.+", url)
    if match is not None:
        print("Chapter not released yet")
        return

    chapter_regex = re.compile('.+\/Boku-No-Hero-Academia-(\d+(-\w*){0,1})(\/.*){0,1}')
    chapter = chapter_regex.match(url).group(1)

    print(">>> in download chapter " + chapter)

    local_chapter_path = "./output/Chapter " + chapter + "/"
    if not os.path.exists(local_chapter_path):
        os.mkdir(local_chapter_path)

    download_page(url, local_chapter_path)
    print("<<< out download chapter " + chapter)

def download_page(url, local_chapter_path):
    print(">>>>>> in download page")
    response = throttled_get_request(url)
    content = html.fromstring(response.content)
    image_url = content.xpath('//img[@id="eatmanga_image"]/@src | //img[@id="eatmanga_image_big"]/@src')[0]

    if image_url is not None:
        save_image_to_disk(image_url, local_chapter_path)
    else:
        print("Could not find image, skipping.");

    # go to next page if possible
    next_page = content.xpath('//div[@class="navigation"]/a[@id="page_next"]/@href')
    if len(next_page) > 0:
        next_page = domain + next_page[0]
        if next_page != 'javascript:void(0);':
            download_page(next_page, local_chapter_path)
    else:
        print("Could not find next page link")
    print("<<<<<< out download page")

def save_image_to_disk(image_url, local_chapter_path):
    local_file_path = local_chapter_path + image_url.split('/')[-1]
    if not os.path.exists(local_file_path):
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            print("Saving " + image_url + " ---> " + local_file_path)
            with open(local_file_path, 'wb') as local_file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, local_file)
    else:
        print(local_file_path + " already exists. Skipping download from server.")

def throttled_get_request(url):
    r = requests.get(url)
    random_wait = (random.random() * 3) + 2
    print("----- waiting " + str(random_wait) + " seconds -----")
    time.sleep(random_wait)
    return r

if __name__ == '__main__':
    main()

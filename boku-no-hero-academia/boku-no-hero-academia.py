import requests
from lxml import html
import shutil
import time
import os
import logging
import re
import random

# logpath = 'results_hero_academia.log'
# if os.path.exists(logpath):
#     pass
# logging.basicConfig(filename=logpath)

domain = "http://eatmanga.com"

def main():
    outputPath = ".\\output\\"
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
        print("Remaining Chapters in List: " + str(len(chapters_list)))

def download_chapter(url):
    match = re.match(".+\/upcoming\/.+", url)
    if match is not None:
        print("Chapter not released yet")
        return

    chapter_regex = re.compile('.+\/Boku-No-Hero-Academia-(\d+(-\w*){0,1})(\/.*){0,1}')
    chapter = chapter_regex.match(url).group(1)
    
    local_chapter_path = ".\\output\\Chapter " + chapter + "\\"
#     incomplete_local_chapter_path = ".\\output\\Chapter " + chapter + " INCOMPLETE\\"
    if os.path.exists(local_chapter_path):
        print('Chapter ' + chapter + ' fully downloaded. Proceeding to next chapter.')
        return
    
    if not os.path.exists(local_chapter_path):
        os.mkdir(local_chapter_path)

    download_page(url, local_chapter_path)
    
#     time.sleep(3)
#     if os.access(incomplete_local_chapter_path, os.W_OK):
#          os.rename(incomplete_local_chapter_path, local_chapter_path)
#     else:
#         print('Could not access folder for renaming. Wait 3 seconds.')
#         time.sleep(3)
#         if os.access(incomplete_local_chapter_path, os.W_OK):
#             os.rename(incomplete_local_chapter_path, local_chapter_path)
#         else:
#             print('Could not access folder for renaming (2nd try). Skipping renaming')

def download_page(url, local_chapter_path):
    response = throttled_get_request(url)
    content = html.fromstring(response.content)
    image_url_list = content.xpath('//img[@id="eatmanga_image"]/@src | //img[@id="eatmanga_image_big"]/@src')
    if len(image_url_list) > 0:
        image_url = image_url_list[0]
        save_image_to_disk(image_url, local_chapter_path)
    else:
        print("Could not find image on page, skipping.");

    # go to next page if possible
    next_page_list = content.xpath('//div[@class="navigation"]/a[@id="page_next"]/@href')
    if len(next_page_list) > 0:
        next_page = next_page_list[0]
        if next_page != 'javascript:void(0);':
            next_page = domain + next_page
            download_page(next_page, local_chapter_path)
        else:
            print("javascript:void(0) found. End of chapter.")
    else:
        print("Could not find next page link. Ending chapter download.")

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
    random_wait = (random.random() * 2) + 1
#     print("----- waiting " + str(random_wait) + " seconds -----")
    time.sleep(random_wait)
    return r

if __name__ == '__main__':
    main()
################################################################################################
import argparse
from glob import glob
from pprint import pprint
from sys import exit, path
import os
from datetime import timedelta
from timeit import timeit
from time import sleep
import inspect
from sys import argv
from selenium.webdriver.common.by import By
from multiprocessing import get_context
import pyautogui
import warnings

path.append("")

import myUtils
import m3u8_downloader

CNYS = 'CNYS'
WJYS = 'WJYS'
CTV = 'CTV'

CNYS_BASE_URL = 'https://cnys.tv/'
WJYS_BASE_URL = 'https://www.wjys.cc/'
CTV_BASE_URL = 'https://c-tv.tv/'

CNYS_SEARCH_URL = CNYS_BASE_URL + 'vodsearch.html?wd={}'
CTV_SEARCH_URL = CTV_BASE_URL + 'tag/?wd={}'
WJYS_SEARCH_URL = WJYS_BASE_URL + 'vodsearch.html?wd={}'

CNYS_SEARCH_PAGE_URL = CNYS_BASE_URL + 'vodsearch-page-{}-wd-{}.html'
CTV_SEARCH_PAGE_URL = CTV_BASE_URL + 'tag/page/{}/wd/{}/'
WJYS_SEARCH_PAGE_URL = WJYS_BASE_URL + 'vodsearch/page/{}/wd/{}.html'

CNYS_VIDEO_URL = CNYS_BASE_URL + 'vodplay-{}-sid-{}-nid-{}.html'
CTV_VIDEO_URL = CTV_BASE_URL + 'dyplay/{}-1-1/'
WJYS_VIDEO_URL = WJYS_BASE_URL + 'vodplay/{}-1-1.html'

CNYS_DETAIL_URL = CNYS_BASE_URL + 'voddetai-{}.html'
CTV_DETAIL_URL = CTV_BASE_URL + 'dy/{}/'
WJYS_DETAIL_URL = WJYS_BASE_URL + 'voddetai-{}.html'

SITE_BASE_URL = {
    'cnys' : CNYS_BASE_URL,
    'wjys' : WJYS_BASE_URL,
    'ctv' : CTV_BASE_URL,
}

SITE_SEARCH_URL = {
    'cnys' : CNYS_SEARCH_URL,
    'wjys' : WJYS_SEARCH_URL,
    'ctv' : CTV_SEARCH_URL,
}

SITE_SEARCH_PAGE_URL = {
    'cnys' : CNYS_SEARCH_PAGE_URL,
    'wjys' : WJYS_SEARCH_PAGE_URL,
    'ctv' : CTV_SEARCH_PAGE_URL,
}

SITE_VIDEO_URL = {
    'cnys' : CNYS_VIDEO_URL,
    'wjys' : WJYS_VIDEO_URL,
    'ctv' : CTV_VIDEO_URL,
}

SITE_DETAIL_URL = {
    'cnys' : CNYS_DETAIL_URL,
    'wjys' : WJYS_DETAIL_URL,
    'ctv' : CTV_DETAIL_URL,
}

DOUBAN_BASE_URL = 'https://movie.douban.com'

################################################################################################
def parseVideoIdCNYS(driver, videoName):
    videoDict = {}
    page = 1
    videoUrl = CNYS_SEARCH_URL.format(videoName)

    while True:
        driver.get(videoUrl)
        titles = myUtils.findElementsByXpath(driver, '//div[@class="thumb-txt cor4 hide"]')
        if not titles:
            break

        descs =  myUtils.findElementsByXpath(driver, '//span[@class="cor5 thumb-blurb hide2"]')
        ids = myUtils.findElementsByXpath(driver, '//a[@class="thumb-s collection fa ds-shoucang"]')
        years = myUtils.findElementsByXpath(driver, '//div[@class="thumb-else cor5 hide"]')
        actors = myUtils.findElementsByXpath(driver, '//div[@class="thumb-actor cor5 hide"]')

        try:
            for title, id, year, actor, desc in zip(titles, ids, years, actors, descs):
                aTags = year.find_elements(By.TAG_NAME, 'a')
                # bTags = director.find_elements(By.TAG_NAME, 'a')
                bTags = actor.find_elements(By.TAG_NAME, 'a')
                if len(aTags) > 2:
                    year, area, category = aTags[0].text, aTags[1].text, aTags[2].text
                elif len(aTags) == 2:
                    year, area, category = aTags[0].text, aTags[1].text, '未知'
                elif len(aTags) == 1:
                    year, area, category = '未知', aTags[0].text, '未知'
                if len(bTags) > 2:
                    actor = f'{bTags[1].text}/{bTags[2].text}'
                elif len(bTags) == 2:
                    actor = bTags[1].text
                else:
                    actor = '未知'
                title = title.text
                desc = desc.text
                videoId = id.get_attribute("data-id")
                # sId = dataId.get_attribute("data-type")
                # nId = dataId.get_attribute("data-mid")
                videoDict[f'CNYS-{videoId}'] = f'{area}-{year}-{category}-{title}-{actor}-{desc}'
        except Exception as e:
            print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
            pass
        page += 1
        videoUrl = CNYS_SEARCH_PAGE_URL.format(page, videoName)
    return videoDict

################################################################################################
def parseVideoIdWJYS(driver, videoName):
    videoDict = {}
    page = 1
    videoUrl = WJYS_SEARCH_URL.format(videoName)

    while True:
        try:
            driver.get(videoUrl)
            sleep(0.5)
            for i in range(1, 3):
                pyautogui.hotkey('ctrl', '+') # zoom +10% for one 

            for i in range(1, 4):
                try:
                    myUtils.elementInvisibleXPath(driver, 60, '//input[@class="verify_submit submit_btn"]')
                    sleep(0.5)
                    break
                except Exception as e:
                    sleep(3)
                    pass

            items = myUtils.findElementsByXpath(driver, '//div[@class="module-search-item"]')
            if len(items) == 0 or not items or items[0].text == '':
                break

            for item in items:
                item1 = myUtils.findElementsByXpath(item, './/a[@class="video-serial"]')
                title = item1[0].get_attribute('title')
                videoId = item1[0].get_attribute('href').split('/')[4].replace('.html', '')
                item2 = myUtils.findElementsByXpath(item, './/a[@class="tag-link"]')
                category = item2[0].get_attribute('title')
                item3 = myUtils.findElementsByXpath(item, './/div[@class="tag-link"]')
                year = item3[0].text[:-1]
                area =item3[1].text[:-1].replace(' ', '/')
                item4 = myUtils.findElementsByXpath(item, './/div[@class="video-info-item video-info-actor"]')
                actor = myUtils.findElementsByTag(item4[0], 'a')[0].text
                actor += '/' + myUtils.findElementsByTag(item4[1], 'a')[0].text
                item5 = myUtils.findElementsByXpath(item, './/div[@class="video-info-item"]')
                desc = item5[0].text
                videoDict[f'WJYS-{int(videoId):06}'] = f'{area}-{year}-{category}-{title}-{actor}-{desc}'
        except Exception as e:
            print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
            pass
        page += 1
        videoUrl = WJYS_SEARCH_PAGE_URL.format(page, videoName)
    return videoDict

################################################################################################
def parseVideoIdCTV(driver, videoName):
    videoDict = {}
    page = 1
    videoUrl = CTV_SEARCH_URL.format(videoName)
    
    while True:
        driver.get(videoUrl)
        details = myUtils.findElementsByXpath(driver, '//div[@class="detail"]')
        if not details:
            break

        for detail in details:
            try:
                titles = myUtils.findElementsByXpath(detail, './/h3[@class="title"]/a')[0]
                videoId = f'{int(titles.get_attribute("href").split("/")[4]):06}'
                title = titles.text
                actor = myUtils.findElementsByTag(detail, 'p')[1].text.split('：')[1].replace(',', '/')
                elements = myUtils.findElementsByXpath(detail, './/p[@class="hidden-mi"]')[0].text.split('：')
                category = elements[1][:-2].replace(' ', '').replace(',', '/')
                area = elements[2][:-2].replace(' ', '').replace(',', '/')
                year = elements[3]
                videoDict[f'C-TV-{videoId}'] = f'{area}-{year}-{category}-{title}-{actor}'
            except Exception as e:
                print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
                pass

        for videoId, value in videoDict.items():
            descUrl = CTV_DETAIL_URL.format(videoId)
            driver.get(descUrl)
            descs = myUtils.findElementsByXpath(driver, '//p[@class="desc hidden-xs"]')
            if descs:
                desc = descs[0].text.replace('简介： ', '').replace(' 详情', '')
                videoDict[videoId] = f'{value}-{desc}'

        page += 1
        videoUrl = CTV_SEARCH_PAGE_URL.format(page, videoName)
    return videoDict

################################################################################################
def parseVideoId(site:str, videoNames):
    videoDict = {}
    headless = 0 if site == 'wjys' or site == 'all' else 1
    driver = myUtils.getFirefoxDriver(headless)

    for videoName in videoNames.split(','):
        if site.upper() == CNYS:
            videoDict.update(parseVideoIdCNYS(driver, videoName))
            sleep(0.5)

        elif site.upper() == WJYS:
            videoDict.update(parseVideoIdWJYS(driver, videoName))
            sleep(0.5)

        elif site.upper() == CTV:
            videoDict.update(parseVideoIdCTV(driver, videoName))
            sleep(0.5)

        else:
            videoDict.update(parseVideoIdCNYS(driver, videoName))
            sleep(1)

            videoDict.update(parseVideoIdWJYS(driver, videoName))
            sleep(1)

            videoDict.update(parseVideoIdCTV(driver, videoName))
            sleep(1)

    driver.quit()
    return videoDict

################################################################################################
def sortDictValue(videoDict):
    return {k : v for k, v in sorted(videoDict.items(), key=lambda x: x[0].split('-')[0] + x[1])}

################################################################################################
def praseEpisodes(driver, videoDict):
    videoDict = sortDictValue(videoDict)
    for i, (videoId, value) in enumerate(videoDict.items()):
        count = 1
        episodeUrl = CNYS_DETAIL_URL.format(videoId)
        driver.get(episodeUrl)
        sleep(.5)
        xPath = '//i[@class="fa ds-dianying"]'
        count = '??'
        myUtils.elementXPath(driver, 60, xPath)
        elements = myUtils.findElementsByXpath(driver, xPath)
        for element in elements:
            if '海外' in element.text:
                count = myUtils.findElementsByXpath(driver, '//span[@class="badge"]')
                count = '01' if not count.isdigit() else count
                break

        value = f'{int(count):02}-{value}'
        videoDict[videoId] = value
        print(f'{i+1:02} {videoId}: {value}')
    return videoDict

################################################################################################
def getUrlsFromJavaScript(driver):
    url, url_next, player_aaaa = '', '', None
    try:
        player_aaaa = driver.execute_script('return player_aaaa')
    except Exception as e:
        pass

    if player_aaaa:
        url = player_aaaa['url']
        if url:
            url_next = player_aaaa['url_next']
    return url, url_next

################################################################################################
def parseUrlListCNYS(base, videoId):
    videoName, year = '', ''
    sId = 1
    page = 1
    urls = {}
    driver = myUtils.getFirefoxDriver()

    try:
        while True:
            link = base.format(videoId, sId, page)
            driver.get(link)

            if not videoName:
                element = myUtils.findElementsByXpath(driver, '//a[@class="player-title-link"]')
                videoName = element[0].text if element else ''

            if not year:
                element1 = myUtils.findElementsByXpath(driver, '//div[@class="player-details flex wrap"]')
                element2 = myUtils.findElementsByTag(element1[0], 'a')
                year = element2[0].text if element2 else '????'

            url, url_next = getUrlsFromJavaScript(driver)
            if not url:
                break

            if sId == 1 and not url.startswith('https://m3u.haiwaikan.com/'):
                sId = 2
                page = 1
                continue
            elif sId == 2 and not url.startswith('https://m3u.haiwaikan.com/'):
                break

            id = f'{page:02}'
            urls[id] = url
            print(f'{id}: {url}')

            if not url_next:
                break

            id = f'{page+1:02}'
            urls[id] = url_next
            print(f'{id}: {url_next}')

            page += 2
    except Exception as e:
        print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
        pass

    driver.quit()
    return videoName, year, urls, sId

################################################################################################
def parseUrlListCTV(base, videoId):
    videoName, year = '', ''
    sId = 1
    page = 1
    urls = {}
    driver = myUtils.getFirefoxDriver()

    try:
        while True:
            link = base.format(videoId)
            driver.get(link)

            if not videoName:
                element = myUtils.findElementsByXpath(driver, '//h1[@class="title"]')
                videoName = element[0].text if element else ''
            
            if not year:
                element1 = myUtils.findElementsByXpath(driver, '//p[@class="data margin-0"]')
                element2 = myUtils.findElementsByTag(element1[0], 'a')
                year = element2[-1].text if element2 else '????'
            
            url, url_next = getUrlsFromJavaScript(driver)
            if not url:
                break

            id = f'{page:02}'
            urls[id] = url
            print(f'{id}: {url}')

            if not url_next:
                break

            id = f'{page+1:02}'
            urls[id] = url_next
            print(f'{id}: {url_next}')

            page += 2
    except Exception as e:
        print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
        pass

    driver.quit()
    return videoName, year, urls, sId

################################################################################################
def parseUrlListWJYS(base, videoId):
    videoName, year = '', ''
    sId = 1
    page = 1
    urls = {}
    driver = myUtils.getFirefoxDriver(headless=0)

    try:
        while True:
            link = base.format(videoId)
            driver.get(link)

            if not videoName:
                element = myUtils.findElementsByXpath(driver, '//h1[@class="page-title"]')
                videoName = element[0].text if element else ''

            if not year:
                element1 = myUtils.findElementsByXpath(driver, '//div[@class="video-info-aux"]')
                element2 = myUtils.findElementsByXpath(element1[0], './/a[@class="tag-link"]')
                year = element2[1].text if element2 else '????'

            url, url_next = getUrlsFromJavaScript(driver)
            if not url:
                break

            id = f'{page:02}'
            urls[id] = url
            print(f'{id}: {url}')

            if not url_next:
                break

            id = f'{page+1:02}'
            urls[id] = url_next
            print(f'{id}: {url_next}')

            page += 2
    except Exception as e:
        print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
        pass
    driver.quit()

    return videoName, year, urls, sId

def downloadFile(url, mergedFolder, filename, count):
    msg = filename if count == 1 else f'{filename[:-4]}/{count:02}'
    print(f'Downloading {msg}...')
    m3u8_downloader.download(url, f'{mergedFolder}/{filename}')

################################################################################################
def downloadVideoFiles(urls, mergedFolder, filename):
    try:
        count = len(urls)
        existsFiles = sorted(list(myUtils.listFiles(mergedFolder, '.mp4', onlyFilename=True, includeSubFolder=False)))
        for key, url in urls.items():
            if 'vip.' in url:
                print(f'Inaccessible url {url}')
                continue
            if not filename:
                filename = f'{key}.mp4'
            if filename in existsFiles:
                print(f'{filename} exists, skip downloading!')
                continue
            downloadFile(url, mergedFolder, filename, count)
    except Exception as e:
        print(f'{__file__}-{inspect.getframeinfo(inspect.currentframe()).lineno}: {e}')
        pass

################################################################################################
def checkArgv():
    site, videoName, videoId, sId, folder, filename = '', '', '', '', '', ''
    count = len(argv)
    if  count <= 1 or count == 4:
        print('1. Search videoIds')
        print(f'Usage: python {argv[0]} site videoName\n')
        print('2 .Download video url list')
        print(f'Usage: python {argv[0]} site videoId\n')
        print('3 .Download drama files to 001.mp4, 002.mp4,...')
        print(f'Usage: python {argv[0]} site videoId sId outputFolder\n')
        print('4 .Download movie file to filename')
        print(f'Usage: python {argv[0]} site videoId sId outputFolder/filename.mp4\n')
    elif count == 2 and argv[1] not in ['all', 'cnys', 'wjys', 'ctv']:
        site = 'all'
        videoName = argv[1]
    elif count == 3:
        if argv[2].isdigit():
            site = argv[1]
            videoId = argv[2]
        else:
            site = argv[1]
            videoName = argv[2]
    elif count >= 5:
        site, videoId, sId, folder = argv[1], argv[2], argv[3], argv[4]
        if folder.endswith('.mp4'):
            filename = os.path.basename(folder)
            folder = os.path.dirname(folder)
    return site, videoName, videoId, sId, folder, filename

def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
def parseUrlList(site:str, videoId):
    if site.upper() == CNYS:
        videoName, year, urls, sId = parseUrlListCNYS(CNYS_VIDEO_URL, videoId)
    elif site.upper() == CTV:
        videoName, year, urls, sId = parseUrlListCTV(CTV_VIDEO_URL, videoId)
    elif site.upper() == WJYS:
        videoName, year, urls, sId = parseUrlListWJYS(WJYS_VIDEO_URL, videoId)
    return videoName, year, urls, sId

################################################################################################
def main():
    site, videoNames, videoId, sId, mergedFolder, filename = checkArgv()
    urls = {}
    
    if videoNames:
        print(f'Search VideoIds for {videoNames}...')
        videoDict = parseVideoId(site, videoNames)

        if videoDict:
            videoDict = sortDictValue(videoDict)
            myUtils.printDict(videoDict)
        else:
            print(f'No videoIds for {videoNames}!')
    elif videoId:
        textFilename = f'**/*{videoId}-{sId}.txt'
        filePaths = glob(textFilename, recursive=True)

        if filePaths:
            urls = myUtils.readDictFromFile(filePaths[0])
        if not urls:
            print(f'Parsing video url list...')
            videoName, year, urls, sId = parseUrlList(site, videoId)

            if urls:
                myUtils.saveDictToFile(f'data/{site.upper()}-{year}-{videoName}-{videoId}-{sId}.txt', urls)
            else:
                print(f'No accessable url list for videoId {videoId}!')
        if urls and mergedFolder:
            downloadVideoFiles(urls, mergedFolder, filename)

################################################################################################
def parseArguments():
    parser = argparse.ArgumentParser(description="Python3 video Id searcher or m3u8 downloader")
    subparser = parser.add_subparsers()
    parser_list = subparser.add_parser('site')
    parser_list.add_argument(
        'site_site', 
        default='all', const='all', nargs='?', choices=['all', 'cnys', 'wjys', 'ctv'],
        help="The site for search, default 'all' for all sites",
    )

    parser.add_argument(
        "title",
        default="",
        type=str,
        help="The title of movie or drama to be searched",
    )

    parser.add_argument(
        "videoId",
        default=0,
        type=int,
        help="The videoId of movie or drama for downloading m3u8 url list"
    )

    parser.add_argument(
        "sid",
        default=0,
        type=int,
        help="The sId of movie or drama for downloading m3u8 url list"
    )

    parser.add_argument(
        "output",
        default="", 
        type=str,
        help="File polder and filename for saved mp4, e.g. /movie/title.mp4," 
             "or /drama to save 01.mp4-99.mp4 to folder /drama, "
             "If not specified, the output file name will be set to current folder"
    )
    return parser
    # args = parser.parse_args()
    # return args

################################################################################################
if __name__ == "__main__":
    # Suppress specific warning
    warnings.filterwarnings("ignore", message="RuntimeWarning: invalid value encountered in exp2")
    
    from multiprocessing import set_start_method
    set_start_method("spawn")

    showRunTime("main()")

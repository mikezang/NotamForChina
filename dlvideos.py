################################################################################################
import argparse
from glob import glob
from pprint import pprint
from sys import exit, path
import os
from datetime import timedelta
from timeit import timeit
from time import sleep
from sys import argv
from selenium.webdriver.common.by import By
# import pyautogui
import warnings

# Suppress specific warning
warnings.filterwarnings("ignore", message="invalid value encountered in exp2")

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

CNYS_ACTOR_URL = CNYS_BASE_URL + 'vodsearch-actor-{}.html'

CNYS_VIDEO_URL = CNYS_BASE_URL + 'vodplay-{}-sid-{}-nid-{}.html'
CTV_VIDEO_URL = CTV_BASE_URL + 'dyplay/{}-1-1/'
WJYS_VIDEO_URL = WJYS_BASE_URL + 'vodplay/{}-{}-{}.html'

CNYS_DETAIL_URL = CNYS_BASE_URL + 'voddetai-{}.html'
CTV_DETAIL_URL = CTV_BASE_URL + 'dy/{}/'
WJYS_DETAIL_URL = WJYS_BASE_URL + 'voddetai-{}.html'

SITE_BASE_URL = {
    CNYS : CNYS_BASE_URL,
    WJYS : WJYS_BASE_URL,
    CTV : CTV_BASE_URL,
}

SITE_SEARCH_URL = {
    CNYS : CNYS_SEARCH_URL,
    WJYS : WJYS_SEARCH_URL,
    CTV : CTV_SEARCH_URL,
}

SITE_SEARCH_PAGE_URL = {
    CNYS : CNYS_SEARCH_PAGE_URL,
    WJYS : WJYS_SEARCH_PAGE_URL,
    CTV : CTV_SEARCH_PAGE_URL,
}

SITE_VIDEO_URL = {
    CNYS : CNYS_VIDEO_URL,
    WJYS : WJYS_VIDEO_URL,
    CTV : CTV_VIDEO_URL,
}

SITE_DETAIL_URL = {
    CNYS : CNYS_DETAIL_URL,
    WJYS : WJYS_DETAIL_URL,
    CTV : CTV_DETAIL_URL,
}

DOUBAN_BASE_URL = 'https://movie.douban.com'

################################################################################################
def parseVideoIdCNYS(driver, videoName):
    videoDict = {}
    page = 1
    videoUrl = CNYS_SEARCH_URL.format(videoName)
    print(f'Search VideoIds for {videoName} on {CNYS_BASE_URL}...')

    while True:
        driver.get(videoUrl)
        titles = myUtils.findElementsByXPath(driver, '//div[@class="thumb-txt cor4 hide"]')
        if not titles:
            break

        descs =  myUtils.findElementsByXPath(driver, '//span[@class="cor5 thumb-blurb hide2"]')
        ids = myUtils.findElementsByXPath(driver, '//a[@class="thumb-s collection fa ds-shoucang"]')
        years = myUtils.findElementsByXPath(driver, '//div[@class="thumb-else cor5 hide"]')
        actors = myUtils.findElementsByXPath(driver, '//div[@class="thumb-actor cor5 hide"]')

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
        except:
            myUtils.pritnExceptionTrace()
            pass
        page += 1
        videoUrl = CNYS_SEARCH_PAGE_URL.format(page, videoName)
    return videoDict

################################################################################################
def parseVideoIdWJYS(driver, videoName):
    videoDict = {}
    page = 1
    videoUrl = WJYS_SEARCH_URL.format(videoName)
    print(f'Search VideoIds for {videoName} on {WJYS_BASE_URL}...')

    while True:
        try:
            driver.get(videoUrl)
            sleep(1)
            # pyautogui.hotkey('ctrl', '+') # zoom +10% for one 

            for i in range(1, 4):
                try:
                    myUtils.elementXPathFocus(driver, '//input[@name="verify"]', True)
                    myUtils.elementInvisibleXPath(driver, 60, '//input[@class="verify_submit submit_btn"]')
                    break
                except:
                    verifyCode = myUtils.findElementsByXPath(driver, '//input[@name="verify"]')
                    if verifyCode:
                        verifyCode[0].clear()
                    sleep(1)
                    pass

            sleep(2)
            items = myUtils.findElementsByXPath(driver, '//div[@class="module-search-item"]')
            if len(items) == 0 or not items or items[0].text == '':
                break

            for item in items:
                item1 = myUtils.findElementsByXPath(item, './/a[@class="video-serial"]')
                title = item1[0].get_attribute('title')
                videoId = item1[0].get_attribute('href').split('/')[4].replace('.html', '')
                item2 = myUtils.findElementsByXPath(item, './/a[@class="tag-link"]')
                category = item2[0].get_attribute('title')
                item3 = myUtils.findElementsByXPath(item, './/div[@class="tag-link"]')
                year = item3[0].text[:-1]
                area =item3[1].text[:-1].replace(' ', '/')
                item4 = myUtils.findElementsByXPath(item, './/div[@class="video-info-item video-info-actor"]')
                actors = item4[1].text.split('/')
                actor = actors[0] if len(actors) == 1 else actors[0] + '/' + actors[1]
                item5 = myUtils.findElementsByXPath(item, './/div[@class="video-info-item"]')
                desc = item5[0].text
                videoDict[f'WJYS-{int(videoId):06}'] = f'{area}-{year}-{category}-{title}-{actor}-{desc}'
        except:
            myUtils.pritnExceptionTrace()
            pass
        page += 1
        videoUrl = WJYS_SEARCH_PAGE_URL.format(page, videoName)
    return videoDict

################################################################################################
def parseVideoIdCTV(driver, videoName):
    videoDict = {}
    page = 1
    videoUrl = CTV_SEARCH_URL.format(videoName)
    print(f'Search VideoIds for {videoName} on {CTV_BASE_URL}...')

    try:
        while True:
            myUtils.setTimeout(driver, 30)
            driver.get(videoUrl)
            details = myUtils.findElementsByXPath(driver, '//div[@class="detail"]')
            if not details:
                break

            for detail in details:
                try:
                    titles = myUtils.findElementsByXPath(detail, './/h3[@class="title"]/a')[0]
                    videoId = f'{int(titles.get_attribute("href").split("/")[4]):06}'
                    title = titles.text
                    actor = myUtils.findElementsByTag(detail, 'p')[1].text.split('：')[1].replace(',', '/')
                    elements = myUtils.findElementsByXPath(detail, './/p[@class="hidden-mi"]')[0].text.split('：')
                    category = elements[1][:-2].replace(' ', '').replace(',', '/')
                    area = elements[2][:-2].replace(' ', '').replace(',', '/')
                    year = elements[3]
                    videoDict[f'C-TV-{videoId}'] = f'{area}-{year}-{category}-{title}-{actor}'
                except:
                    myUtils.pritnExceptionTrace()
                    pass

            for videoId, value in videoDict.items():
                descUrl = CTV_DETAIL_URL.format(videoId)
                driver.get(descUrl)
                descs = myUtils.findElementsByXPath(driver, '//p[@class="desc hidden-xs"]')
                if descs:
                    desc = descs[0].text.replace('简介： ', '').replace(' 详情', '')
                    videoDict[videoId] = f'{value}-{desc}'

            page += 1
            videoUrl = CTV_SEARCH_PAGE_URL.format(page, videoName)
    except:
        pass
    return videoDict

################################################################################################
def parseVideoId(site:str, videoNames):
    videoDict = {}
    site = site.upper()

    for videoName in videoNames.split(','):
        if site == CNYS:
            driver = myUtils.getFirefoxDriver()
            videoDict.update(parseVideoIdCNYS(driver, videoName))
        elif site == CTV:
            driver = myUtils.getFirefoxDriver()
            videoDict.update(parseVideoIdCTV(driver, videoName))
        elif site == WJYS:
            driver = myUtils.getFirefoxDriver(0)
            videoDict.update(parseVideoIdWJYS(driver, videoName))
        else:
            driver = myUtils.getFirefoxDriver()
            videoDict.update(parseVideoIdCNYS(driver, videoName))
            sleep(0.5)

            videoDict.update(parseVideoIdCTV(driver, videoName))
            sleep(0.5)

            driver.quit()
            driver = myUtils.getFirefoxDriver(0, False)
            videoDict.update(parseVideoIdWJYS(driver, videoName))
        sleep(0.5)

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
        elements = myUtils.findElementsByXPath(driver, xPath)
        for element in elements:
            if '海外' in element.text:
                count = myUtils.findElementsByXPath(driver, '//span[@class="badge"]')
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
    except:
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
    print(f'Parsing {videoId} url list on {CNYS_BASE_URL}...')

    try:
        while True:
            link = base.format(videoId, sId, page)
            driver.get(link)

            if not videoName:
                element = myUtils.findElementsByXPath(driver, '//a[@class="player-title-link"]')
                videoName = element[0].text if element else ''

            if not year:
                element1 = myUtils.findElementsByXPath(driver, '//div[@class="player-details flex wrap"]')
                if not element1:
                    break

                element2 = myUtils.findElementsByTag(element1[0], 'a')
                year = element2[0].text if element2 else '????'

            url, url_next = getUrlsFromJavaScript(driver)
            if not url:
                break

            if not url.startswith('https://m3u.haiwaikan.com/'):
                page = 1
                sId += 1
                if sId > 3:
                    break
                else:
                    continue

            id = f'{page:02}'
            urls[id] = url
            print(f'{id}: {url}')

            if not url_next:
                break

            id = f'{page+1:02}'
            urls[id] = url_next
            print(f'{id}: {url_next}')

            page += 2
    except:
        myUtils.pritnExceptionTrace()
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
    print(f'Parsing {videoId} url list on {CTV_BASE_URL}...')

    try:
        while True:
            link = base.format(videoId)
            driver.get(link)

            if not videoName:
                element = myUtils.findElementsByXPath(driver, '//h1[@class="title"]')
                videoName = element[0].text if element else ''
            
            if not year:
                element1 = myUtils.findElementsByXPath(driver, '//p[@class="data margin-0"]')
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
    except:
        myUtils.pritnExceptionTrace()
        pass

    driver.quit()
    return videoName, year, urls, sId

################################################################################################
def parseUrlListWJYS(base, videoId, sId):
    videoName, year = '', ''
    page = 1
    urls = {}
    driver = myUtils.getFirefoxDriver(0, False)
    print(f'Parsing {videoId} url list on {WJYS_BASE_URL}...')

    try:
        tabIndex = 0
        link = base.format(videoId, sId, page)
        driver.get(link)
        tabs = myUtils.findElementsByXPath(driver, '//a[@class="module-tab-item tab-item"]')

        while True:
            if not videoName:
                element = myUtils.findElementsByXPath(driver, '//h1[@class="page-title"]')
                videoName = element[0].text if element else ''

            if not year:
                element1 = myUtils.findElementsByXPath(driver, '//div[@class="video-info-aux"]')
                element2 = myUtils.findElementsByXPath(element1[0], './/a[@class="tag-link"]')
                year = element2[1].text if element2 else '????'

            # TODO loop to multiple tabls for not vip url
            url, url_next = getUrlsFromJavaScript(driver)
            if not url:
                break

            if not 'vip.' in url:
                id = f'{page:02}'
                urls[id] = url
                print(f'{id}: {url}')

                if not url_next:
                    break

                id = f'{page+1:02}'
                urls[id] = url_next
                print(f'{id}: {url_next}')

                page += 2
                link = base.format(videoId, sId, page)
                driver.get(link)
            else:
                link = tabs[tabIndex].get_property('href')
                driver.get(link)
                tabIndex += 1
    except:
        myUtils.pritnExceptionTrace()
        # print(f'{__file__}: {os.linesep} + {traceback.format_exc()}')
        pass
    driver.quit()
    return videoName, year, urls, sId

################################################################################################
def downloadVideoFiles(urls, mergedFolder, filename):
    try:
        count = len(urls)
        existsFiles = sorted(list(myUtils.listFiles(mergedFolder, '.mp4', onlyFilename=True, includeSubFolder=False)))
        for key, url in urls.items():
            if 'vip.' in url:
                print(f'Inaccessible url {url}')
            else:
                if not filename:
                    filename = f'{key}.mp4'
                if filename in existsFiles:
                    print(f'{filename} exists, skip downloading!')
                else:
                    msg = filename if count == 1 else f'{filename[:-4]}/{count:02}={int(filename[:-4]) * 100 // count}%'
                    print(f'Downloading {msg}...')
                    m3u8_downloader.download(url, f'{mergedFolder}/{filename}')
            filename = ''
    except:
        myUtils.pritnExceptionTrace()
        pass

################################################################################################
def checkArgv():
    site, videoName, videoId, sId, folder, filename = '', '', '', '2', '', ''
    count = len(argv)
    if  count <= 1:
        print('1. Search videoIds')
        print(f'Usage: python {argv[0]} site videoName\n')
        print('2 .Download video url list')
        print(f'Usage: python {argv[0]} site videoId\n')
        print('3 .Download drama files to 001.mp4, 002.mp4,...')
        print(f'Usage: python {argv[0]} site videoId sId outputFolder\n')
        print('4 .Download movie file to filename')
        print(f'Usage: python {argv[0]} site videoId sId outputFolder/filename.mp4\n')
    elif count == 2 and argv[1] not in ['all', CNYS, WJYS, CTV]:
        site = 'all'
        videoName = argv[1]
    elif count == 3:
        if argv[2].isdigit():
            site = argv[1].upper()
            videoId = argv[2]
        else:
            site = argv[1].upper()
            videoName = argv[2]
    elif count == 4:
        if argv[2].isdigit():
            site = argv[1].upper()
            videoId = argv[2]
            sId = argv[3]
    elif count >= 5:
        site, videoId, sId, folder = argv[1].upper(), argv[2], argv[3], argv[4]
        if folder.endswith('.mp4'):
            filename = os.path.basename(folder)
            folder = os.path.dirname(folder)
    return site, videoName, videoId, sId, folder, filename

def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'Finished in {timedelta(seconds=result)}\n')

################################################################################################
def parseUrlList(site:str, videoId, sId):
    if site.upper() == CNYS:
        videoName, year, urls, sId = parseUrlListCNYS(CNYS_VIDEO_URL, videoId)
    elif site.upper() == CTV:
        videoName, year, urls, sId = parseUrlListCTV(CTV_VIDEO_URL, videoId)
    elif site.upper() == WJYS:
        videoName, year, urls, sId = parseUrlListWJYS(WJYS_VIDEO_URL, videoId, sId)
    return videoName, year, urls, sId

################################################################################################
def main():
    site, videoNames, videoId, sId, mergedFolder, filename = checkArgv()
    urls = {}
    
    if videoNames:
        videoDict = parseVideoId(site, videoNames)

        if videoDict:
            videoDict = sortDictValue(videoDict)
            myUtils.printDict(videoDict)
        else:
            print(f'No videoIds for {videoNames}!')
    elif videoId:
        if mergedFolder != '':
            textFilename = f'**/*{videoId}-{sId}.txt'
            filePaths = glob(textFilename, recursive=True)
        else:
            filePaths = ''
        if filePaths:
            urls = myUtils.readDictFromFile(filePaths[0])
        if not urls:
            videoName, year, urls, sId = parseUrlList(site, videoId, sId)

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
        default='all', const='all', nargs='?', choices=['all', CNYS, WJYS, CTV],
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
    from multiprocessing import set_start_method
    set_start_method("spawn")

    showRunTime("main()")

################################################################################################
import argparse
from glob import glob
from os import path
from datetime import timedelta
from timeit import timeit
from time import sleep
from sys import argv
import warnings

# Suppress specific warning
warnings.filterwarnings("ignore", message="invalid value encountered in exp2")

from myModules import myUtils
from myModules import myNet
from myModules import myExcept
from myModules import m3u8_downloader

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
def parseVideoIdCNYS(driver, videoName: str) -> dict:
    videoDict = {}
    page = 1
    videoUrl = CNYS_SEARCH_URL.format(videoName)
    print(f'Search VideoIds for {videoName} on {CNYS_BASE_URL}...')

    while True:
        driver.get(videoUrl)
        titles = myNet.findElementsByXPath(driver, '//div[@class="thumb-txt cor4 hide"]')
        if not titles:
            break

        descs =  myNet.findElementsByXPath(driver, '//span[@class="cor5 thumb-blurb hide2"]')
        ids = myNet.findElementsByXPath(driver, '//a[@class="thumb-s collection fa ds-shoucang"]')
        years = myNet.findElementsByXPath(driver, '//div[@class="thumb-else cor5 hide"]')
        actors = myNet.findElementsByXPath(driver, '//div[@class="thumb-actor cor5 hide"]')

        try:
            for title, id, year, actor, desc in zip(titles, ids, years, actors, descs):
                # aTags = year.find_elements(By.TAG_NAME, 'a')
                # bTags = actor.find_elements(By.TAG_NAME, 'a')
                aTags = myNet.findElementsByTag(year, 'a')
                bTags = myNet.findElementsByTag(actor, 'a')
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
            myExcept.printExceptionTrace()
            pass
        page += 1
        videoUrl = CNYS_SEARCH_PAGE_URL.format(page, videoName)
    return videoDict

################################################################################################
def parseVideoIdWJYS(driver, videoName: str) -> dict:
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
                    myNet.elementXPathFocus(driver, '//input[@name="verify"]', True)
                    myNet.elementInvisibleXPath(driver, 60, '//input[@class="verify_submit submit_btn"]')
                    break
                except:
                    verifyCode = myNet.findElementsByXPath(driver, '//input[@name="verify"]')
                    if verifyCode:
                        verifyCode[0].clear()
                    sleep(1)
                    pass

            sleep(2)
            items = myNet.findElementsByXPath(driver, '//div[@class="module-search-item"]')
            if len(items) == 0 or not items or items[0].text == '':
                break

            for item in items:
                item1 = myNet.findElementsByXPath(item, './/a[@class="video-serial"]')
                title = item1[0].get_attribute('title')
                videoId = item1[0].get_attribute('href').split('/')[4].replace('.html', '')
                item2 = myNet.findElementsByXPath(item, './/a[@class="tag-link"]')
                category = item2[0].get_attribute('title')
                item3 = myNet.findElementsByXPath(item, './/div[@class="tag-link"]')
                year = item3[0].text[:-1]
                area =item3[1].text[:-1].replace(' ', '/')
                item4 = myNet.findElementsByXPath(item, './/div[@class="video-info-item video-info-actor"]')
                actors = item4[1].text.split('/')
                actor = actors[0] if len(actors) == 1 else actors[0] + '/' + actors[1]
                item5 = myNet.findElementsByXPath(item, './/div[@class="video-info-item"]')
                desc = item5[0].text
                videoDict[f'WJYS-{int(videoId):06}'] = f'{area}-{year}-{category}-{title}-{actor}-{desc}'
        except:
            myExcept.printExceptionTrace()
            pass
        page += 1
        videoUrl = WJYS_SEARCH_PAGE_URL.format(page, videoName)
    return videoDict

################################################################################################
def parseVideoIdCTV(driver, videoName: str) -> dict:
    videoDict = {}
    page = 1
    videoUrl = CTV_SEARCH_URL.format(videoName)
    print(f'Search VideoIds for {videoName} on {CTV_BASE_URL}...')

    try:
        while True:
            myNet.setTimeout(driver, 30)
            driver.get(videoUrl)
            details = myNet.findElementsByXPath(driver, '//div[@class="detail"]')
            if not details:
                break

            for detail in details:
                try:
                    titles = myNet.findElementsByXPath(detail, './/h3[@class="title"]/a')[0]
                    videoId = f'{int(titles.get_attribute("href").split("/")[4]):06}'
                    title = titles.text
                    actor = myNet.findElementsByTag(detail, 'p')[1].text.split('：')[1].replace(',', '/')
                    elements = myNet.findElementsByXPath(detail, './/p[@class="hidden-mi"]')[0].text.split('：')
                    category = elements[1][:-2].replace(' ', '').replace(',', '/')
                    area = elements[2][:-2].replace(' ', '').replace(',', '/')
                    year = elements[3]
                    videoDict[f'C-TV-{videoId}'] = f'{area}-{year}-{category}-{title}-{actor}'
                except:
                    myExcept.printExceptionTrace()
                    pass

            for videoId, value in videoDict.items():
                descUrl = CTV_DETAIL_URL.format(videoId)
                driver.get(descUrl)
                descs = myNet.findElementsByXPath(driver, '//p[@class="desc hidden-xs"]')
                if descs:
                    desc = descs[0].text.replace('简介： ', '').replace(' 详情', '')
                    videoDict[videoId] = f'{value}-{desc}'

            page += 1
            videoUrl = CTV_SEARCH_PAGE_URL.format(page, videoName)
    except:
        pass
    return videoDict

################################################################################################
def parseVideoId(site:str, videoNames:str) -> dict:
    videoDict = {}
    site = site.upper()

    if site == CNYS:
        driver = myNet.getFirefoxDriver()
        for videoName in videoNames.split(','):
            videoDict.update(parseVideoIdCNYS(driver, videoName))
    elif site == CTV:
        driver = myNet.getFirefoxDriver()
        for videoName in videoNames.split(','):
            videoDict.update(parseVideoIdCTV(driver, videoName))
    elif site == WJYS:
        driver = myNet.getFirefoxDriver(0)
        for videoName in videoNames.split(','):
            videoDict.update(parseVideoIdWJYS(driver, videoName))
    else:
        driver = myNet.getFirefoxDriver()
        for videoName in videoNames.split(','):
            videoDict.update(parseVideoIdCNYS(driver, videoName))
            sleep(0.5)

            videoDict.update(parseVideoIdCTV(driver, videoName))
            sleep(0.5)

        driver.quit()
        driver = myNet.getFirefoxDriver(0, False)
        for videoName in videoNames.split(','):
            videoDict.update(parseVideoIdWJYS(driver, videoName))
            sleep(0.5)
    driver.quit()
    return videoDict

################################################################################################
def sortDictValue(videoDict: dict) -> dict:
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
        myNet.elementXPath(driver, 60, xPath)
        elements = myNet.findElementsByXPath(driver, xPath)
        for element in elements:
            if '海外' in element.text:
                count = myNet.findElementsByXPath(driver, '//span[@class="badge"]')
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
    driver = myNet.getFirefoxDriver()
    print(f'Parsing {videoId} url list on {CNYS_BASE_URL}...')

    try:
        while True:
            link = base.format(videoId, sId, page)
            driver.get(link)

            if not videoName:
                element = myNet.findElementsByXPath(driver, '//a[@class="player-title-link"]')
                videoName = element[0].text if element else ''

            if not year:
                element1 = myNet.findElementsByXPath(driver, '//div[@class="player-details flex wrap"]')
                if not element1:
                    break

                element2 = myNet.findElementsByTag(element1[0], 'a')
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
        myExcept.printExceptionTrace()
        pass

    driver.quit()
    return videoName, year, urls, sId

################################################################################################
def parseUrlListCTV(base: str, videoId: int):
    videoName, year = '', ''
    sId = 1
    page = 1
    urls = {}
    driver = myNet.getFirefoxDriver()
    print(f'Parsing {videoId} url list on {CTV_BASE_URL}...')

    try:
        while True:
            link = base.format(videoId)
            driver.get(link)

            if not videoName:
                element = myNet.findElementsByXPath(driver, '//h1[@class="title"]')
                videoName = element[0].text if element else ''
            
            if not year:
                element1 = myNet.findElementsByXPath(driver, '//p[@class="data margin-0"]')
                element2 = myNet.findElementsByTag(element1[0], 'a')
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
        myExcept.printExceptionTrace()
        pass

    driver.quit()
    return videoName, year, urls, sId

################################################################################################
def parseUrlListWJYS(base: str, videoId: int, sId: int) -> list:
    videoName, year = '', ''
    page = 1
    urls = {}
    driver = myNet.getFirefoxDriver(1)
    print(f'Parsing {videoId} url list on {WJYS_BASE_URL}...')

    try:
        tabIndex = 0
        link = base.format(videoId, sId, page)
        driver.get(link)
        tabs = myNet.findElementsByXPath(driver, '//a[@class="module-tab-item tab-item"]')
        href = ''
        for i, tab in enumerate(tabs):
            href += tab.get_property('href').split('-')[1] + ', '
        print(f'sIds: {href}')

        while True:
            if not videoName:
                element = myNet.findElementsByXPath(driver, '//h1[@class="page-title"]')
                videoName = element[0].text if element else ''

            if not year:
                element1 = myNet.findElementsByXPath(driver, '//div[@class="video-info-aux"]')
                element2 = myNet.findElementsByXPath(element1[0], './/a[@class="tag-link"]')
                year = element2[1].text if element2 else '????'

            url, url_next = getUrlsFromJavaScript(driver)
            if not url:
                break

            if not 'vip' in url:
                id = f'{page:02}'
                urls[id] = url
                print(f'{sId}-{id}: {url}')

                if not url_next:
                    break

                id = f'{page+1:02}'
                urls[id] = url_next
                print(f'{sId}-{id}: {url_next}')

                page += 2
                link = base.format(videoId, sId, page)
                driver.get(link)
            else:
                tabIndex += 1
                if len(tabs) > tabIndex:
                    # loop to multiple tabls for not vip url
                    link = tabs[tabIndex].get_property('href')
                    links = link.split('-')
                    sId = links[1]
                    driver.get(link)
                else:
                    break
    except:
        myExcept.printExceptionTrace()
        pass
    driver.quit()
    return videoName, year, urls, sId

def downloadMP4(url: str, key: str, filename: str, count: int, existFiles: list, mergedFolder: str):
    if not filename:
        filename = f'{key}.mp4'
    if filename in existFiles:
        print(f'{filename} exists, skip downloading!')
    else:
        msg = filename if count == 1 else f'{filename[:-4]}/{count:02}={int(filename[:-4]) * 100 // count}%'
        print(f'Downloading {msg}...')
        m3u8_downloader.download(url, f'{mergedFolder}/{filename}')

################################################################################################
def downloadVideoFiles(urls: dict, mergedFolder:str, filename: str, reverse=False) -> None:
    try:
        count = len(urls)
        existFiles = sorted(list(myUtils.listFiles(mergedFolder, '.mp4', onlyFilename=True, includeSubFolder=False)))
        if reverse:
            for key, url in reversed(urls.items()):
                if 'vip.' in url:
                    print(f'Inaccessible url {url}')
                    break
                downloadMP4(url, key, filename, count, existFiles, mergedFolder)
                filename = ''
        else:
            for key, url in urls.items():
                if 'vip.' in url:
                    print(f'Inaccessible url {url}')
                    break
                downloadMP4(url, key, filename, count, existFiles, mergedFolder)
                filename = ''
    except:
        myExcept.printExceptionTrace()
        pass

################################################################################################
def showUsage():
    print('1. Search videoIds')
    print(f'Usage: python {argv[0]} site videoName\n')
    print('2 .Download video url list')
    print(f'Usage: python {argv[0]} site videoId\n')
    print('3 .Download drama files to 001.mp4, 002.mp4,...')
    print(f'Usage: python {argv[0]} site videoId sId outputFolder\n')
    print('4 .Download movie file to filename')
    print(f'Usage: python {argv[0]} site videoId sId outputFolder/filename.mp4\n')

################################################################################################
def checkArgv() -> list:
    site, videoName, videoIds, sId, folder, filename = '', '', '', '2', '', ''
    count = len(argv)
    if  count <= 1:
        showUsage()
    elif count == 2 and argv[1] not in ['all', CNYS, WJYS, CTV]:
        site = 'all'
        videoName = argv[1]
    elif count == 3:
        if argv[2].isdigit():
            site = argv[1].upper()
            videoIds = argv[2]
        else:
            site = argv[1].upper()
            videoName = argv[2]
    elif count == 4:
        if argv[2].isdigit():
            site = argv[1].upper()
            videoIds = argv[2]
            sId = argv[3]
    elif count >= 5:
        site, videoIds, sId, folder = argv[1].upper(), argv[2], argv[3], argv[4]
        if folder.endswith('.mp4'):
            filename = path.basename(folder)
            folder = path.dirname(folder)
        if not folder.startswith('/'):
            folder = f'/Users/mikezang/movies/{folder}'
    else:
        showUsage()
    return site, videoName, videoIds, sId, folder, filename

def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'Finished in {timedelta(seconds=result)}\n')

################################################################################################
def parseUrlList(site:str, videoId: int, sId: int) -> list:
    if site.upper() == CNYS:
        videoName, year, urls, sId = parseUrlListCNYS(CNYS_VIDEO_URL, videoId)
    elif site.upper() == CTV:
        videoName, year, urls, sId = parseUrlListCTV(CTV_VIDEO_URL, videoId)
    elif site.upper() == WJYS:
        videoName, year, urls, sId = parseUrlListWJYS(WJYS_VIDEO_URL, videoId, sId)
    return videoName, year, urls, sId

################################################################################################
def main() -> None:
    site, videoNames, videoIds, sId, mergedFolder, filename = checkArgv()
    if site not in ['all', CNYS, WJYS, CTV]:
        print(f"The site is not in ['all', {CNYS}, {WJYS}, {CTV}]")
        showUsage()
        return
    videoId = videoIds if videoIds == '' or videoIds[0] != '-' else videoIds[1:]
    urls = {}
    
    if videoNames:
        videoDict = parseVideoId(site, videoNames)

        if videoDict:
            videoDict = sortDictValue(videoDict)
            myUtils.printDict(videoDict)
            myUtils.saveDictToTextFile(f'/tmp/{videoNames}.txt', videoDict)
        else:
            print(f'No videoIds for {videoNames}!')
    elif videoIds:
        if mergedFolder != '':
            textFilename = f'/tmp/*{videoId}-{sId}.txt'
            filePaths = glob(textFilename, recursive=True)
        else:
            filePaths = ''
        if filePaths:
            urls = myUtils.readDictFromFile(filePaths[0])
        if not urls:
            videoName, year, urls, sId = parseUrlList(site, videoId, sId)

            if urls:
                myUtils.saveDictToFile(f'/tmp/{site.upper()}-{year}-{videoName}-{videoId}-{sId}.txt', urls)
            else:
                print(f'No accessable url list for videoId {videoId}!')
    if urls and mergedFolder:
        downloadVideoFiles(urls, mergedFolder, filename, videoIds[0] == '-')
        myUtils.playSound()

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
        help="File folder and filename for saved mp4, e.g. /movie/title.mp4," 
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

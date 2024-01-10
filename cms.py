from sys import argv, path
import os
# from math import degrees
from datetime import datetime, timedelta, timezone
import zoneinfo
from timeit import timeit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox import service as fs
from selenium.webdriver.support.ui import WebDriverWait
import pyorbital.orbital
import pytz
from fake_useragent import UserAgent

path.append("")
import myUtils

TIMEZONE_SHANGHAI = zoneinfo.ZoneInfo('Asia/Shanghai')
TIMEZONE_UTC = pytz.timezone('UTC')
FILE_PATH = './data'

def getChinaTime(d, fmt=None):
    if d.tzinfo is None:
        d = TIMEZONE_UTC.localize(d)

    if fmt:
        return d.astimezone(TIMEZONE_SHANGHAI).strftime(fmt)
    else:
        return d.astimezone(TIMEZONE_SHANGHAI)

def calculate_passes(line1, line2, locDict, startDate=None, hours=100):
    ret = {}

    # Create a pyorbital Orbital object with the given TLE lines
    orb = pyorbital.orbital.Orbital("CMS", line1=line1, line2=line2)
    
    # Get the current time in UTC
    now = datetime.utcnow() if startDate is None else startDate
    _, _, alt = orb.get_lonlatalt(now)
    ret[now] = alt

    for loc in locDict:
        ret[loc] = []
        # Calculate the next 10 passes of the satellite over the specified location
        passes = orb.get_next_passes(utc_time=now, length=hours, lat=locDict[loc][0], lon=locDict[loc][1], alt=0.01)
        
        # Print the pass information for each pass
        for p in passes:
            start_time =p[0]
            end_time = p[1]
            duration = p[2]
            azimuth, elevation = orb.get_observer_look(duration, lon=locDict[loc][1], lat=locDict[loc][0], alt=0.01)
            ret[loc].append([getChinaTime(start_time), getChinaTime(end_time), getChinaTime(duration), azimuth, elevation])
    return ret

def downloadTLE():
    print('下载TLE数据...')
    ua = UserAgent()
    userAgent = ua.random
    options = FirefoxOptions()
    options.headless = True
    options.add_argument('--headless')
    options.set_preference("general.useragent.override", userAgent)
    service = fs.Service(log_path=os.path.devnull)
    driver = webdriver.Firefox(options=options, service=service)

    try:
        CMS_URL = 'http://www.cmse.gov.cn/gfgg/zgkjzgdcs/'
        driver.set_page_load_timeout(123)
        driver.get(CMS_URL)

        XPATH_DIV = '//div[@class="TRS_Editor"]'
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, XPATH_DIV)))
        divs = driver.find_elements(By.XPATH, XPATH_DIV)
        tle = []

        for div in divs:
            if div.text:
                divList = div.text.split('\n')
                for d in divList:
                    tle.append(f'{d}\n')
                    # print(d)
                break
        driver.close()
        if tle:
            updateTLEFile(tle, f'{FILE_PATH}/tle{myUtils.getJapanDate()}.txt')
            # saveTLEToFile(tle, f'{FILE_PATH}/tle{myUtils.getJapanDate()}.txt')
    except Exception as e:
        # print(e)
        print('下载TEL失败！')
        print('使用既存TLE数据...')
        tle = readTLEFromFile()
    return tle

def updateTLEFile(tle, filename):
    if tle != readTLEFromFile():
        saveTLEToFile(tle, filename)

def saveTLEToFile(tle, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for l in tle:
            f.write(f'{l}')

def readTLEFromFile():
    tle = []
    fileList = list(myUtils.listFiles(FILE_PATH, '.txt'))
    filename = fileList[-1]
    with open(filename, 'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            tle.append(line)
            line = f.readline()
    return tle

def convertDMS(decimal_degrees):
    degrees, decimal_minutes = divmod(decimal_degrees, 1)
    minutes, decimal_seconds = divmod(decimal_minutes * 60, 1)
    seconds, _ = divmod(decimal_seconds * 60, 1)
    return degrees, minutes, seconds

def convertAzimuth(azimuth):
    azimuthChinese = ['正北', '东北偏北', '东北', '东北偏东', '正东', '东南偏东', '东南', '东南偏南', 
                      '正南', '西南偏南', '西南', '西南偏西', '正西', '西北偏西', '西北', '西北偏北']
    i = int(((azimuth + 11.25) % 360) / 22.5)
    return azimuthChinese[i]

def showTime(startDate, passTime, hours, tle):
    # print(f'计算中国空间站{startDate.year}年{startDate.month}月{startDate.day}日开始{hours}小时经过酒泉/文昌时间...')

    for i, key in enumerate(passTime):
        if i == 0:
            now, alt = key, passTime[key]
            text = f"根据最新轨道参数TLE\n{tle[0]}{tle[1]}中国空间站（轨道周期约92.2分）"
            text += f"{getChinaTime(now, '%Y-%m-%d %H:%M')}位于{int(alt)}公里太空："
            print(text)
        else:
            loc, values = key, passTime[key]
            print(f"{startDate.year}年{startDate.month}月{startDate.day}日开始{hours}小时内将于下列时日通过{loc}上空(仰角大于45°)：")
            # values = sorted(values, key=lambda x: x[3], reverse=True)

            for value in values:
                start_time, end_time, duration, azimuth, elevation = value
                if elevation > 75:
                    degree1, minute1, second1 = convertDMS(elevation)
                    # degree2, minute2, second2 = convertDMS(azimuth)
                    pass_date1 = start_time.date()
                    pass_time1 = start_time.time()
                    pass_date2 = end_time.date()
                    pass_time2 = end_time.time()
                    pass_date = duration.date()
                    pass_time = duration.time()
                    d1 = f'{pass_date1.year}年{pass_date1.month:02}月{pass_date1.day:02}日'
                    t1 = f'{pass_time1.hour:02}时{pass_time1.minute:02}分'
                    d2 = f'{pass_date2.year}年{pass_date2.month:02}月{pass_date2.day:02}日'
                    t2 = f'{pass_time2.hour:02}时{pass_time2.minute:02}分'
                    d = f'{pass_date.year}年{pass_date.month:02}月{pass_date.day:02}日'
                    t = f'{pass_time.hour:02}时{pass_time.minute:02}分'
                    text = f"\t{d}{t}，仰角：{degree1:02.0f}°{minute1:02.0f}'{second1:02.0f}\"，"
                    text += f"方位角：{convertAzimuth(azimuth)}"
                    print(text)
            print()

def main():
    startDate = datetime.utcnow()
    if len(argv) >= 2:
        if len(argv[1]) != 8:
            print(f'Usage: cms [YYYYMMDD] [hours]')
            print(f'\t[YYYYMMDD] default is current date')
            print(f'\t[hours] default is 100 hours')
            return
        
        year = int(argv[1][:4])
        month = int(argv[1][4:6])
        day = int(argv[1][6:8])
        # startDate = datetime(year, month, day, tzinfo=pytz.UTC)
        startDate = datetime(year, month, day, tzinfo=TIMEZONE_SHANGHAI).astimezone(timezone.utc)

    hours = 200
    if len(argv) >= 3:
        hours = int(argv[2])

    tle = downloadTLE()

    if not tle:
        print('没有TEL数据！')
        return
    
    locations = {'酒泉' :(40.9667, 100.3), '西昌': (28.25, 102.03333), '文昌': (19.6167, 110.95)}
    passTime = calculate_passes(tle[0], tle[1], locations, startDate, hours)
    showTime(startDate, passTime, hours, tle)


def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    showRunTime("main()")


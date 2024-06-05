"""
    Thie is constants
"""
# pylint: disable=C0103,C0115,C0116,C0301

import pytz

HEADLESS = 1

header = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_3) "
                  "AppleWebKit/602.4.8 (KHTML, like Gecko) Version"
                  "/10.0.3 Safari/602.4.8"
}

PROXY_ID = "zhengrong.zang@smflc.co.jp"
PROXY_PW = "ABC#123def"

BUTTON1_LABEL = '统计条形图作成'
BUTTON2_LABEL = '动态条形图作成'

COMMANDS = {
    "Location" : "//input[@ng-model='$parent.globalScope.designatorsForLocation']",
    "Free Text" : "//input[@ng-model='$parent.globalScope.freeFormText']",
    "Archive Search" : "",
    "all" : "",
    "ctrip" : "",
    "eniutrip" : "",
    "nsf" : "",
    "nsfurls" : "",
    "nsfnotams" : "",
    "nsfmaps" : "",
    "nsfcontents" : "",
    "fir" : "",
    "compare" : "",
    "kml" : "",
    "test" : "",
}

FREE_TEXTS = (
    "RJJJ",
    "AEROSPACE",
    "TEMPORARY DANGER AREA ESTABLISHED",
    "TEMPORARY RESTRICTED AREA ESTABLISHED BOUNDED",
    "CHINA NATIONAL SPACE ADMINISTRATION",
    "FLW SEGMENT OF ATS RTE CLSD",
    "SPACEFLIGHT",
    "CHINESE",
    "SPACE FLIGHT",
    "TEMPO DANGER AREA ACTIVATED IN AREA BOUNDED",
    "AERO SPACE",
    #"TEMPORARY PROHIBITED AREA ESTABLISHED",
)

COL_LOCATION = 1
COL_NUMBER = 2
COL_START_DATE_UTC = 4
COL_END_DATE_UTC = 5
COL_CONDITION = 6

NEW_NOTAM_URL = "https://www.notams.faa.gov/dinsQueryWeb/"
NEW_CSS_SELECTOR_BUTTON_DISCLAIMER = ".ui-state-default.ui-corner-all"
NEW_XPATH_RADIO_TYPE = "//input[@name='reportType' and @value='Raw']"
NEW_XPATH_TEXTAREA = "//textarea[@name='retrieveLocId']"
NEW_XPATH_SEARCH_BUTTON = "//input[@name='submit' and @value='View NOTAMs']"

NOTAM_URL = "https://notams.aim.faa.gov/notamSearch/nsapp.html#/"

XPATH_DIV_HIDE1 = "//div[@class='modal-backdrop fade']"
XPATH_DIV_HIDE2 = "//div[@class='modal fade bootstrap-dialog type-primary size-normal']"
XPATH_DIV_HIDE3 = "//div[@class='modal fade bootstrap-dialog type-primary size-normal in']"

XPATH_INPUT_USERNAME = "//input[@id='username_input']"
XPATH_INPUT_SUBMIT = "//input[@type='submit']"
XPATH_INPUT_PASSWORD = "//input[@name='passsfc']"
XPATH_SPAN_DETAIL = "//span[@ng-bind-html='globalScope.selectedNOTAM.icaoMessage']"
XPATH_BUTTON_DISCLAIMER = "//button[@ng-click='agreeDisclaimerDoNotChangeUrl();checkDisclaimer();']"
XPATH_BUTTON_SEARCH = "//button[@ng-click='globalScope.clearIgnoredLocations();globalScope.clearFilters(false);globalScope.searchNotams(false, false);']"
XPATH_SELECT_TYPE = "//select[@ng-model='globalScope.searchType']"
XPATH_SELECT_BUTTON = "//button[@data-toggle='dropdown']"
XPATH_SELECT_OPTION = "//select[@ng-model='globalScope.searchType']/option[text()='{0}']"
XPATH_TRS_NOTAM = "//tr[@ng-if='globalScope.wwidth>=768']"
XPATH_TD_NOTAM = ".//child::td"
XPATH_TTABLE_NOTAM = "//table[@class='table table-striped table-hover table-bordered table-condensed table-responsive']"
XPATH_SEARCH_RESULT = "//span[@ng-click='globalScope.criteriaExpanded=!globalScope.criteriaExpanded;']"
XPATH_TD_SPAN = "//span[@ng-bind-html='globalScope.getConditionHtml(notam.traditionalMessageFrom4thWord);']"
XPATH_BUTTON_BACK = "//button[@ng-click='backToResults();']"

PRINT_NOTAM_LENGTH = 118
PRINT_NSF_LENGTH = 120

TIMEZONE_BEIJING = 'Asia/Shanghai'
TIMEZONE_TOKYO = 'Asia/Tokyo'
TIMEZONE_BEIJING1 = pytz.timezone('Asia/Shanghai')
TIMEZONE_TOKYO1 = pytz.timezone('Asia/Tokyo')
TIMEZONE__UTC = pytz.timezone('UTC')

KML_FOLDERS = {
    '酒泉' : r'notams/maps/01.酒泉',
    '西昌' : r'notams/maps/02.西昌',
    '太原' : r'notams/maps/03.太原',
    '文昌' : r'notams/maps/04.文昌',
    '海南' : r'notams/maps/05.海南',
    '海上' : r'notams/maps/10.海上',
    '黄海' : r'notams/maps/10.海上',
    '东海' : r'notams/maps/10.海上',
    '南海' : r'notams/maps/10.海上',
}

EXCEL_COLUMN_ROCKET = '火箭'
EXCEL_COLUMN_NUMBER = '序号'
EXCEL_COLUMN_DATE = '日期'
EXCEL_COLUMN_LOCATION = '地点'
EXCEL_COLUMN_SPOT = '工位'
EXCEL_COLUMN_RESULT = '结果'
EXCEL_COLUMN_PAYLOAD = '载荷'
EXCEL_COLUMN_REMARKS = '备注'

PATTERN1 = r'([NS]\d{4,6}[EW]\d{5,7})'        #N1234E12345/N123456E1234567/S1234E12345/S123456E1234567
PATTERN3 = r'(\d{4,6}\.?\d{0,2}[NS] ?\d{5,7}\.?\d{0,2}[EW])'        #1234N12345E/123456N1234567E/1234S12345E/123456S1234567E
PATTERN5 = r'(\d{4,6}\.\d{1,2}[NS]\d{4,7}\.\d{1,2}[EW])'       #123456.1S1234567.1E/123456.1S123456.1E, 023800.00N0920000.00E
PATTERN6 = r'(\d{4,6}[NS]\/\d{5,7}[EW])'                    #0104N/14436E
PATTERN7 = r'(\d{2}[°-]\d{2}[′.-]?\d{0,3}″?[NS][ \/]?\d{2,3}[°-]\d{2}[′.-]?\d{0,3}″?[EW])'#37-53-79N120-18-58E/37-53.7N120-18.5E/13°33′46″N ，117°57′26″E

PATTERNS = (
    PATTERN1,
    PATTERN3,
    PATTERN5,
    PATTERN6,
    PATTERN7,
)

PATTERN_LATITUDE_LONGITUDE =  r'([NS]\d{4,6}[EW]\d{5,7}|'
PATTERN_LATITUDE_LONGITUDE += r'\d{4,6}\.?\d{0,2}[NS]\d{5,7}\.?\d{0,2}[EW]|'
PATTERN_LATITUDE_LONGITUDE += r'\d{4,6}\.\d{1,2}[NS]\d{5,7}\.\d{1,2}[EW]|'
PATTERN_LATITUDE_LONGITUDE += r'\d{4,6}[NS]\/\d{5,7}[EW])'
# PATTERN_LATITUDE_LONGITUDE += PATTERN7 #
PATTERM_QUESTION = r'/(\d{4,6}[NS]\d{5,7}[EW])\d{3}'

# MSA_PATTERN_LATITUDE_LONGITUDE = r'(\d{2}\-\d{2}[.-]\d{2}[NS])(\d{3}\-\d{2}[.-]\d{2}[EW])'
# MSA_PATTERN_LATITUDE_LONGITUDE = r'(\d{2}[°-]\d{2}[′.-]\d{1,3}"?[NS])/?(\d{2,3}[°-]\d{2}[′.-]\d{1,3}"?[EW])'
MSA_PATTERN_LATITUDE_LONGITUDE =  r'(\d{2}[°-]\d{2}[\′.-]?\d{0,3}″?[NS][ \/]?\d{2,3}[°-]\d{2}[′.-]?\d{0,3}"?[EW])'
MSA_PATTERN_LATITUDE_LONGITUDE1 = r'(\d{2}[°-]\d{2}[′.-]\d{1,3}″?[NS]/?\d{2,3}[°-]\d{2}[′.-]\d{1,3}"?[EW])'
MSA_PATTERN_DATE = r'FROM(\d{0,2})(\d{0,4})[UTC]{0,3}([A-Z]{0,4})\.?(\d{0,2})TO(\d{0,2})(\d{0,4})[UTC]{0,3}([A-Z]{0,4})\.?(\d{0,2})'
MSA_PATTERN_NUMBER = r'([A-Z][A-Z]|鲁航警)(\d{1,3}\/\d{2})'

# MSA_PATTERN_DATE_CHINA1 = r'(\d{1,2})月(\d{1,4})日(\d{1,4})时至(\d{1,4})时'
MSA_PATTERN_DATE_CHINA = r'(?:(\d{1,2})月)?(\d{1,2})日(?:(\d{1,4})时)?至(?:(\d{1,2})月)?(?:(\d{1,2})日)?(?:(\d{1,4})时)?'

# Color for launch center
# color is reverse order from google map
COLOR_JIUQUAN = "ff1427a5"
COLOR_TAIYUAN = "ff0051e6"
COLOR_XICHANG = "ff25a8f9"
COLOR_WENCHANG = "ff2f8b55"
COLOR_HAINAN = "ff2f8b55"
COLOR_SEA = "ffAB4939" #"ff9b5701"

# Latitude and Longitude for laucnh center
COODINATE_JIUQUAN = "100.3,40.96666666666667"
COODINATE_TAIYUAN = "111.604815,38.84257"
COODINATE_XICHANG = "102.03333,28.25"
COODINATE_WENCHANG = "110.95,19.616666666666667"
COODINATE_HAINAN = "110.95,19.616666666666667"
COODINATE_HAIYANG = "121°14'15\",36°40'40\""

CITIES = {
    "酒泉" : f"酒泉|{COODINATE_JIUQUAN}|{COLOR_JIUQUAN}",
    "太原" : f"太原|{COODINATE_TAIYUAN}|{COLOR_TAIYUAN}",
    "西昌" : f"西昌|{COODINATE_XICHANG}|{COLOR_XICHANG}",
    "文昌" : f"文昌|{COODINATE_WENCHANG}|{COLOR_WENCHANG}",
    "海南" : f"海南|{COODINATE_HAINAN}|{COLOR_HAINAN}",
    "海阳" : f"海阳|{COODINATE_HAIYANG}",
    "海上" : f"海上|,|{COLOR_SEA}",
    "黄海" : f"黄海|,|{COLOR_SEA}",
    "东海" : f"东海|,|{COLOR_SEA}",
    "南海" : f"南海|,|{COLOR_SEA}",
    "东风航天城" : f"酒泉|{COODINATE_JIUQUAN}|{COLOR_JIUQUAN}",
}

NSF_URL_CHINA = "https://forum.nasaspaceflight.com/index.php?board=40."
NSF_URL_BASE = 'https://forum.nasaspaceflight.com/index.php?topic='
NSF_PAGE_HEADER = r'OrionSpaceXCommercialISSInternationalOtherShopHomeHelpTagsCalendarLoginRegisterForums'

XPATH_NSF_DETAIL = "//form[@id='quickModForm']"

NSF_DATE_FORMAT = r'((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Sept|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?))'

NOTAM_NUMBER_ERROR = r'1345/16'
NOTAM_NUMBER_INVALID = r'C1832/19'
PATTERN_NOTAM_NUMBER = r'[^R]([A-Z]\d{4}/\d{2}|1345/16)[^.0]'
PATTERN_NOTAM_NUMBER_NEW = r'([A-Z]\d{4}/\d{2})'
# PATTERN_NOTAM_NUMBER = PATTERN_NOTAM_NUMBER = r'[^R]([A-Z]\d{4}/\d{2}|1345/16)[^.0(]'

HYDROPAC_PATTERN = 'MSACHINA|HAZARDOUS|ROCKETLAUNCHING|ROCKETLAUNCHSCHEDULED' #r'HYDROPAC(\d{4}/\d{2})'
HYDROPAC_PATTERN_DATES = r'(\d{1,2})(\d{4})Z([A-Z]{0,3})TO(\d{1,2})(\d{4})Z?([A-Z]{3})'
HYDROPAC_PATTERN_DATES1 = r'(\d{2})([A-Z]{3})(\d{2})FROM(\d{4})UTCTO(\d{4})UTC'

HAZARDOUS_PATTERN_START = 'HAZARDOUS'
ROCKETLAUNCHING_START = 'ROCKETLAUNCHING'
ROCKETLAUNCHSCHEDULED = 'ROCKETLAUNCHSCHEDULED'
# 01FEB21FROM0800UTCTO0930UTC
# 01FEB21FROM0800UTCTO0930UTC

MSA_PATTERN_START = 'HAZARDOUS|ROCKETLAUNCHING|ROCKETLAUNCHSCHEDULED'
MSA_PATTERN_END = 'MSACHINA'

MSA_PATTERN_DATE2_START = r'validity([a-zA-Z]{3,10})(\d{1,2}),(\d{4})UTCto([a-zA-Z]{3,10})(\d{1,2}),(\d{4})'
MSA_PATTERN_DATE2_END = r'(Totaltowinglength:500meters;speed:5knots)'

PATTERN_START_DATE = r'B\)(\d{10})'
PATTERN_END_DATE = r'C\)(\d{10})'
PATTERN_START_END_DATE1 = r'(\d{1,2}[a-zA-Z]+\d{2}:\d{2}\d{4})UNTIL(\d{1,2}[a-zA-Z]+\d{2}:\d{2}\d{4})'
PATTERN_START_END_DATE2 = r'FROM(\d{4}UTC\d{2}[a-zA-Z]+\d{4})TO(\d{4}UTC\d{1,2}[a-zA-Z]+\d{4})'
PATTERN_START_DATE1 = r'(\d{1,2}[a-zA-Z]+\d{2}:\d{2}\d{4})UNTIL'
PATTERN_END_DATE1 = r'UNTIL(\d{2}[a-zA-Z]+\d{2}:\d{2}\d{4})'
#PATTERN_START_DATE1 = r'(\d{1,2}[a-zA-Z]+\d{2}:\d{2}\d{4})UNTIL\d{1,2}[a-zA-Z]+\d{2}:\d{2}\d{4}'
#PATTERN_END_DATE1 = r'\d{2}[a-zA-Z]+\d{2}:\d{2}\d{4}UNTIL(\d{2}[a-zA-Z]+\d{2}:\d{2}\d{4})'
PATTERN_START_DATE2 = r'FROM(\d{4}UTC\d{2}[a-zA-Z]+\d{4})TO\d{4}UTC\d{1,2}[a-zA-Z]+\d{4}'
PATTERN_END_DATE2 = r'FROM\d{4}UTC\d{2}[a-zA-Z]+\d{4}TO(\d{4}UTC\d{1,2}[a-zA-Z]+\d{4})'
PATTERN_START_DATE3 = r'from(\d{4}hourson[a-zA-Z]\d{1,2})to\d{4}hourson[a-zA-Z]\d{1,2}'
PATTERN_END_DATE3 = r'from\d{4}hourson[a-zA-Z]\d{1,2}to(\d{4}hourson[a-zA-Z]\d{1,2})'
PATTERN_START_DATES = f'{PATTERN_START_DATE}|{PATTERN_START_DATE1}|{PATTERN_START_DATE2}'
PATTERN_END_DATES = f'{PATTERN_END_DATE}|{PATTERN_END_DATE1}|{PATTERN_END_DATE2}'


FORMAT_DATE = {
    r'\d{10}' : '%y%m%d%H%M',                               #2210281419
    r'\d{1,2}[a-zA-Z]+\d{2}:\d{2}\d{4}' : '%d%b%H:%M%Y',    #23AUG02:242022
    r'\d{4}UTC\d{1,2}[a-zA-Z]+\d{4}' : '%H%MUTC%d%b%Y',     #1203UTC28SEPT2022
    r'\d{4}[a-zA-Z]\d{1,2}' : '%H%M%B%d',                   #1300September25
}

NSF_DATE_FORMATS = (
    '%B%dth%H:%M,%Y',       #October7th16:10,2022
    '%B%d,%Y-%H:%MUTC',     #October7,2022-16:11UTC
    '%B%d,%Y-%H%MUTC',      #October7,2022-1611UTC
    '%B%d%Y%H%MUTC',        #October720221611UTC
    '%B%d%Y%H:%MUTC',       #October7202216:11UTC
    '%B%d%Y(%H:%MUTC)',     #October72022(16:11UTC)
    '%B%d%Y(%H%MUTC)',      #October72022(1611UTC)
    '%B%d,%Y%H:%MUTC',      #October7,202216:11UTC
    '%B%d,%Y%H:%M:%SUTC',   #October7,202216:11:23UTC
    '%B%d,%Y,%H%MUTC',      #December18,2012,1613UTC
    '%B%d,%Y(%H%MUTC)',     #December28,2015(1604UTC)
    '%B%d,%Y(%H:%MUTC)',    #December28,2015(16:04UTC)
    '%B%d,%Y(%H:%M:%SUTC)',
    '%B%d,%Y(%H:%M:%S.%fUTC)',
    '%B%d,%Y,%H:%MUTC',
    '%b%d%Y(~%H:%MUTC)',    #Sept.42020(~07:30UTC)
    '%d%b%Y~%H:%MUTC',      #30October2022~19:43UTC
    '%b%d%Y%H%MUTC',
    '%b%d%Y%H:%MUTC',
    '%b%d,%Y(%H:%MUTC)',
    '%b%d,%Y(%H:%M:%SUTC)',
    '%b%d,%Y%H:%MUTC',
    '%b%d,%Y%H:%M:%SUTC',
    '%b.%d.%Y(%H:%MUTC)',
    '%b.%d,%Y(%H:%MUTC)',
    '%d%B%Y(%H:%MUTC)',
    '%d%B,%Y(%H:%M:%SUTC)',
    '%d%b%y(%H:%MUTC)',
    '%d%b%Y(%H:%MUTC)',
    '%H:%M,%B%d,%Y',        #00:15,September4,2014
    '%H:%MUTC,%B%d,%Y',     #05:28UTC,September28,2014
)

NSF_CITY_PATTERN = r'(Jiuquan|Taiyuan|Xichang|Wenchang|JSLC|TSLC|XSLC|WSLC|Yellow Sea|E. China Sea)'
NSF_CITIES = {
    "Haiyang" : "海陽",
    "JIUQUAN" : "酒泉",
    "TAIYUAN" : "太原",
    "XICHANG" : "西昌",
    "WENCHANG" : "文昌",
    "YELLOW SEA" : "黄海",
    "E. CHINA SEA" : "东海",
    "JSLC" : "酒泉",
    "TSLC" : "太原",
    "XSLC" : "西昌",
    "WSLC" : "文昌",
}

NSF_FAILURE = "FAILURE"

NSF_ROCKET_PATTERN = r'(cz-2[C-F]|cz-3[A-C]|cz-4[B-C]|cz-5B?|cz-6A?|cz-7A?|cz-8|cz-11H?|long march[ -]2[C-F]|long march[ -]3[A-C]|long march[ -]4[B-C]|long march[ -]5B?|long march[ -]6A?|long march[ -]7A?|long march[ -]8|long march[ -]11H?|KZ-1A?|Kuaizhou-1A?|KZ-11|KuaiZhou-11|Gushenxing-1|GSX-1|Shuangquxian-1|SQX-1|Lijian-1|Jielong-[1-3]|Zhuque-[1-2]|OS-M1|Kaituo-2)'
NSF_ROCKETS = {
    "cz-2c" : "長征二号丙",
    "cz-2d" : "長征二号丁",
    "cz-2f" : "長征二号己",
    "cz-3a" : "長征三号甲",
    "cz-3b" : "長征三号乙",
    "cz-3c" : "長征三号丙",
    "cz-4b" : "長征四号乙",
    "cz-4c" : "長征四号丙",
    "cz-5b" : "長征五号乙",
    "cz-5" : "長征五号",
    "cz-6a" : "長征六号甲",
    "cz-6" : "長征六号",
    "cz-7a" : "長征七号甲",
    "cz-7" : "長征七号",
    "cz-8" : "長征八号",
    "cz-11h" : "長征十一号海",
    "cz-11" : "長征十一号",
    "long march 2c" : "長征二号丙",
    "long march 2d" : "長征二号丁",
    "long march 3a" : "長征三号甲",
    "long march-3a" : "長征三号甲",
    "long march 3b" : "長征三号乙",
    "long march-3b" : "長征三号乙",
    "long march 3c" : "長征三号丙",
    "long march 4b" : "長征四号乙",
    "long march-4b" : "長征四号乙",
    "long march 4c" : "長征四号丙",
    "long march 5b" : "長征五号乙",
    "long march 5" : "長征五号",
    "long march 6a" : "長征六号甲",
    "long march 6" : "長征六号",
    "long march-6" : "長征六号",
    "long march 7a" : "長征七号甲",
    "long march 7" : "長征七号",
    "long march 8" : "長征八号",
    "long march 11h" : "長征十一号海",
    "long march 11" : "長征十一号",
    "long march-11" : "長征十一号",
    "kz-11" : "快舟十一号",
    "kuaizhou-11" : "快舟十一号",
    "kz-1a" : "快舟一号甲",
    "kz-1" : "快舟一号",
    "kuaizhou-1a" : "快舟一号甲",
    "kuaizhou-1" : "快舟一号",
    "gushenxing-1" : "谷神星一号",
    "gsx-1" : "谷神星一号",
    "shuangquxian-1" : "双曲线一号",
    "sqx-1" : "双曲线一号",
    "lijian-1" : "力箭一号",
    "jielong-1" : "捷龙一号",
    "jielong-3" : "捷龙三号",
    "zhuque-1" : "朱雀一号",
    "zhuque-2" : "朱雀二号",
    "os-m1" : "OS-M一号",
    "kaituo-2" : "开拓者二号",
}

FIR_BOUNDARY = {
    'ZBPE' : (
        (43.25000, 117.5167), (39.90000, 119.3500), (39.50000, 119.8667), (38.25000, 120.1000),
        (37.48333, 117.5000), (36.53333, 115.3000), (36.35000, 114.9167), (36.10000, 114.3500),
        (34.90000, 112.7833), (34.00000, 110.4833), (34.53333, 110.2500), (35.53333, 110.3000),
        (37.46667, 110.7333), (38.36666, 110.6000), (38.73333, 109.6833), (40.33333, 107.0167),
        (40.71667, 105.9167), (41.74361, 105.2180), (45.38806, 115.3542),
    ),
    'ZSHA' : (
        (36.53333, 115.3000), (37.48333, 117.5000), (38.25000, 120.0000), (38.00000, 124.0000),
        (30.00000, 124.0000), (29.00000, 124.0000), (25.00000, 120.0000), (23.00000, 117.5000),
        (23.16667, 117.5000), (23.50000, 117.5000), (23.67861, 117.2211), (23.70000, 117.1833),
        (24.36667, 116.7000), (24.76667, 115.0167), (25.11667, 114.3000), (26.05000, 114.1167),
        (26.70000, 113.9500), (29.03333, 114.5667), (30.08333, 115.9333), (32.90000, 115.7833),
        (35.25000, 115.4500), (35.70000, 115.0167), (36.35000, 114.9167),
    ),
    'ZLHW' : (
        (41.74361, 105.2180), (40.71667, 105.9167), (40.33333, 107.0167), (38.73333, 109.6833),
        (38.36667, 110.6000), (37.46667, 110.7333), (35.53333, 110.3000), (34.53333, 110.2500),
        (34.00000, 110.4833), (33.53333, 110.8667), (31.90000, 109.5167), (32.23333, 107.4000),
        (32.45000, 105.8167), (32.91667, 101.7000), (31.81667, 98.58333), (32.00000, 97.00000),
        (32.86667, 91.91667), (38.35000, 90.21667), (41.80000, 95.13333), (42.90694, 96.35693),
    ),
    'ZPKM' : (
        (38.35000, 90.21667), (32.86667, 91.91667), (32.00000, 97.00000), (31.81667, 98.58333),
        (32.91667, 101.7000), (32.45000, 105.8167), (32.23333, 107.4000), (31.90000, 109.5167),
        (30.28333, 109.4833), (29.51667, 109.4000), (27.88333, 109.3167), (26.68333, 109.2000),
        (25.41667, 107.8833), (24.65000, 105.8000), (23.18307, 105.5274), (21.55916, 100.3738),
        (26.92344, 98.54487), (29.39346, 95.26851), (27.55214, 91.70599), (28.86047, 85.02317),
        (30.11532, 81.15649),
    ),
    'ZHWH' : (
        (33.53333, 110.8667), (34.00000, 110.4833), (34.90000, 112.7833), (36.10000, 114.3500),
        (36.35000, 114.9167), (35.70000, 115.0167), (35.25000, 115.4500), (32.90000, 115.7833),
        (30.08333, 115.9333), (29.03333, 114.5667), (29.38333, 113.1000), (29.51667, 109.4000),
        (30.28333, 109.4833), (31.90000, 109.5167),
    ),
    'ZGZU' : (
        (21.41667, 111.5000), (20.50000, 111.5000), (20.50000, 108.0500), (23.18307, 105.5274),
        (24.65000, 105.8000), (25.41667, 107.8833), (26.68333, 109.2000), (27.88333, 109.3167),
        (29.51667, 109.4000), (29.38333, 113.1000), (29.03333, 114.5667), (26.70000, 113.9500),
        (26.05000, 114.1167), (25.11667, 114.3000), (24.76667, 115.0167), (24.36667, 116.7000),
        (23.70000, 117.1833), (23.67861, 117.2211),
    ),
    'RJJJ' : (
        (45.00000, 150.0000), (50.08333, 159.0000), (45.70000, 162.9167), (43.00000, 165.0000),
        (27.00000, 165.0000), (27.00000, 155.0000), (21.00000, 155.0000), (21.00000, 130.0000),
        (21.00000, 121.5000), (23.50000, 124.0000), (29.00000, 124.0000), (30.00000, 124.0000),
        (30.00000, 125.4167), (32.50000, 126.8333), (32.50000, 127.5000), (34.66666, 129.1667),
        (37.50000, 133.0000), (38.63333, 133.6500), (40.50000, 135.9333), (45.75000, 140.0000),
        (45.75000, 142.0000), (44.50000, 145.6667), (44.45000, 145.7333), (43.33333, 145.8333),
        (43.20000, 146.2167), (43.00000, 146.8333), (45.00000, 150.0000),
    ),
    'VHHK' : (
        (23.00000, 117.5000), (21.00000, 117.5000), (19.50000, 111.5000), (21.41667, 111.5000),
        (23.67861, 117.2211), (23.50000, 117.5000), (23.16667, 117.5000),
    ),
    'ZJSA' : (
        (20.50000, 108.0500), (20.50000, 111.5000), (19.50000, 111.5000), (16.66667, 114.00000),
        (14.50000, 114.0000), (14.50000, 112.0000), (18.34111, 107.6814), (19.26778, 107.18972),
        (19.95917, 107.9297), (20.50000, 108.0500),
    ),
    'VYYF' : (
        (29.39346, 95.26851), (26.92344, 98.54487), (21.55916, 100.3738), (19.16060, 97.53789),
        (12.09129, 99.47350), (9.933333, 98.55000), (10.00000, 96.00000), (11.00000, 94.41667),
        (13.50000, 94.41667), (14.00000, 92.00000), (20.00000, 92.00000), (21.00000, 92.00000),
        (21.95000, 92.53333),
    ),
    'VVHM' : (
        (10.36667, 103.7333), (9.000000, 102.6667), (7.000000, 103.0000), (7.000000, 108.0000),
        (10.50000, 114.0000), (16.66667, 114.0000), (17.00000, 114.2500), (17.00000, 111.5000),
        (17.66667, 109.6667), (17.21667, 108.0000), (17.00000, 107.3000), (17.00000, 106.4000),
    ),
    'VVHN' : (
        (20.50000, 108.0500), (19.95000, 107.9333), (19.26667, 107.1833), (18.33333, 107.6833),
        (17.41667, 108.7167), (17.21667, 108.0000), (17.00000, 106.5667), (22.54762, 103.4766),
        (23.18333, 105.5333),
    ),
    'RPHI' : (
        (21.00000, 117.5000), (21.00000, 121.5000), (21.00000, 130.0000), (7.000000, 130.0000),
        (3.500000, 133.0000), (3.500000, 132.0000), (4.000000, 132.0000), (4.000000, 120.0000),
        (7.500000, 117.5000), (8.416667, 116.5000), (10.50000, 114.0000), (14.50000, 114.0000),
        (16.66667, 114.0000),
    ),
    'KZAK' : (
        (0.000000, 140.0000), (0.000000, 180.0000), (48.00000, 180.0000), (45.70000, 162.9167),
        (43.00000, 165.0000), (27.00000, 165.0000), (27.00000, 155.0000), (21.00000, 155.0000),
        (21.00000, 130.0000), (7.000000, 130.0000), (3.500000, 133.0000),
    ),
    'RKRR' : (
        (38.63333, 133.6500), (38.00000, 133.0000), (37.50000, 133.0000), (34.66667, 129.1667),
        (32.50000, 127.5000), (32.50000, 126.8333), (30.00000, 125.4167), (30.00000, 124.0000),
        (38.00000, 124.0000), (38.63333, 128.4167),
    ),
    'YBBB' : (
        (-14.1369, 115.1422), (-12.0000, 114.5000), (-12.0000, 123.3333), (-9.03333, 126.8333),
        (-7.00000, 135.0000), (-9.83333, 139.6666), (-9.83333, 141.0000), (-9.61666, 141.0183),
        (-9.26166, 142.0583), (-9.21333, 142.1066), (-9.19833, 142.1433), (-9.20000, 142.1716),
        (-9.19000, 142.2149), (-9.19333, 142.2349), (-9.23166, 142.2733), (-9.26833, 142.3450),
        (-9.36833, 142.4949), (-9.36333, 142.5250), (-9.37666, 142.5583), (-9.35666, 142.5916),
        (-9.34000, 142.6950), (-9.33833, 142.7316), (-9.32333, 142.8050), (-9.13333, 143.8750),
        (-9.40000, 144.2333), (-9.94277, 144.0891), (-10.0875, 143.9811), (-10.1472, 143.9530),
        (-10.2975, 143.9125), (-10.3788, 143.9236), (-10.4438, 143.9066), (-10.5194, 143.9113),
        (-10.5825, 143.9266), (-10.6872, 143.9694), (-10.7780, 143.9997), (-10.8680, 144.0127),
        (-10.9833, 144.0333), (-11.0400, 144.0425), (-11.1102, 144.0641), (-11.1852, 144.0725),
        (-11.2369, 144.0605), (-11.2527, 144.0519), (-11.4930, 144.0252), (-11.5000, 144.0266),
        (-11.7250, 144.0722), (-12.0000, 144.0000), (-12.0000, 155.0000), (-14.0000, 155.0000),
        (-14.0000, 161.2500), (-17.6666, 163.0000), (-45.0000, 163.0000), (-45.0000, 150.0000),
        (-44.5658, 150.0000), (-43.8508, 150.6647), (-43.0000, 151.0000), (-38.1886, 150.3205),
        (-36.9452, 150.7508), (-34.9500, 150.5333), (-35.3163, 152.9305), (-34.4727, 151.8247),
        (-33.9438, 151.1825), (-33.4274, 150.5297), (-32.0944, 148.8308), (-29.0000, 146.5333),
        (-29.0000, 143.5000), (-26.2252, 138.3900), (-22.2975, 136.6352), (-21.8588, 136.3736),
        (-21.4997, 136.3288), (-21.2025, 131.8400), (-23.2202, 128.4636), (-23.3969, 126.0588),
        (-21.5219, 124.5511), (-20.0550, 121.6727), (-19.0000, 120.2500),
    ),
    'YMMM' : (
        (-6.00000, 75.00000), (-2.00000, 78.00000), (-2.00000, 92.00000), (-12.00000, 107.0000),
        (-12.0000, 114.5000), (-14.1369, 115.1422), (-19.0000, 120.2500), (-20.05500, 121.6728),
        (-21.5219, 124.5511), (-23.3969, 126.0589), (-23.2203, 128.4636), (-21.20250, 131.8400),
        (-21.4997, 136.3289), (-21.8589, 136.3736), (-22.2975, 136.6353), (-26.22528, 138.3900),
        (-29.0000, 143.5000), (-29.0000, 146.5333), (-32.0944, 148.8308), (-33.42750, 150.5297),
        (-33.9439, 151.1825), (-34.4728, 151.8247), (-35.3169, 152.9306), (-34.95000, 150.5333),
        (-36.9453, 150.7508), (-38.1886, 150.3206), (-43.0000, 151.0000), (-43.85083, 150.6647),
        (-44.5658, 150.0000), (-45.0000, 150.0000), (-45.0000, 163.0000), (-45.00000, 163.00000),
        (-45.0000, 75.00000),
    ),
    'NFFF' : (
        (-31.6666, 163.0000), (-17.6666, 163.0000), (-8.31121, 177.2404), (-11.2689, -168.351),
        (-25.1183, -168.351)

    ),
    'VCCF' : (
        (6.733333, 77.95000), (7.000000, 78.50000), (10.00000, 80.00000), (10.00000, 82.00000),
        (6.000000, 92.00000), (-2.00000, 92.00000), (-2.00000, 78.00000), (6.000000, 78.00000),
        (6.000000, 76.50000),
    ),
    'VOMF' : (
        (18.00000, 76.0000), (19.31666, 76.0000), (19.71666, 77.1667), (18.71666, 82.0000),
        (18.68333, 82.8167), (15.70000, 85.9000), (14.00000, 92.0000), (13.50000, 94.4167),
        (6.000000, 94.4167), (6.000000, 92.0000), (10.00000, 82.0000), (10.00000, 80.0000),
        (6.000000, 78.0000), (6.000000, 74.0000), (7.500000, 74.0000), (7.500000, 72.0000),
        (15.00000, 72.0000), (15.00000, 73.5833), (16.28333, 73.0000), (16.36667, 73.5667),
        (16.43333, 74.1833), (16.60000, 75.4667), (16.66667, 76.0000),
    ),
    'ZYSH' : (
        (39.82806, 124.1683), (38.0000, 124.0000), (38.25000, 123.0000), (38.25000, 120.0000),
        (39.50000, 119.8667), (39.9000, 119.3500), (43.24500, 117.5167), (45.38806, 115.3542),
        (54.05430, 122.6381), (47.3087, 134.4497),
    ),
    'ZWUQ' : (
        (42.90694, 96.35693), (41.80000, 95.13333), (38.35000, 90.21667), (30.42500, 81.62331),
        (39.45483, 73.65569), (49.37124, 87.02515),
    ),
}

MUSIC_NAME_DICT = {
    'music/歌唱祖国音乐.mp3': 181.76,
    'music/momoe/001-としごろ.mp3': 159.268571,
    'music/momoe/002-叱らないでね.mp3': 162.168163,
    'music/momoe/003-ひとりぼっちのあなた.mp3': 184.894694,
    'music/momoe/004-青い果実.mp3': 150.151837,
    'music/momoe/005-おかしな恋人.mp3': 149.263673,
    'music/momoe/006-パパは恋人.mp3': 165.433469,
    'music/momoe/007-禁じられた遊び.mp3': 182.909388,
    'music/momoe/008-悩み多い14才.mp3': 145.789388,
    'music/momoe/009-春風のいたずら.mp3': 168.097959,
    'music/momoe/010-雨に濡れた少女.mp3': 190.92898,
    'music/momoe/011-15才の恋.mp3': 167.523265,
    'music/momoe/012-ひと夏の経験.mp3': 159.111837,
    'music/momoe/013-太陽の友達.mp3': 191.164082,
    'music/momoe/014-まばたきの夏.mp3': 147.043265,
    'music/momoe/015-教室を出たら大人.mp3': 172.094694,
    'music/momoe/016-ちっぽけな感傷.mp3': 184.058776,
    'music/momoe/017-清潔な恋.mp3': 196.91102,
    'music/momoe/018-冬の色.mp3': 181.890612,
    'music/momoe/019-伊豆の踊り子.mp3': 184.032653,
    'music/momoe/020-野菊の墓.mp3': 169.822041,
    'music/momoe/021-聖少女.mp3': 221.152653,
    'music/momoe/022-湖の決心.mp3': 197.250612,
    'music/momoe/023-春の奇蹟.mp3': 173.244082,
    'music/momoe/024-少年の海(出逢い).mp3': 216.137143,
    'music/momoe/025-美(み)え貝.mp3': 156.577959,
    'music/momoe/026-初恋時代.mp3': 169.560816,
    'music/momoe/027-夏ひらく青春.mp3': 188.577959,
    'music/momoe/028-ささやかな欲望.mp3': 199.88898,
    'music/momoe/029-ありがとうあなた.mp3': 216.346122,
    'music/momoe/030-白い約束.mp3': 224.470204,
    'music/momoe/031-山鳩.mp3': 185.70449,
    'music/momoe/032-空はこんなに青い.mp3': 202.527347,
    'music/momoe/033-愛に走って.mp3': 219.559184,
    'music/momoe/034-赤い運命.mp3': 192.078367,
    'music/momoe/035-木漏れ日.mp3': 225.201633,
    'music/momoe/036-碧色の瞳.mp3': 205.714286,
    'music/momoe/037-横須賀ストーリー.mp3': 232.306939,
    'music/momoe/038-GAME_IS_OVER.mp3': 211.983673,
    'music/momoe/039-陽炎(かげろう).mp3': 258.246531,
    'music/momoe/040-いま目覚めた子供のように.mp3': 234.945306,
    'music/momoe/041-パールカラーにゆれて.mp3': 188.003265,
    'music/momoe/042-赤い衝撃.mp3': 213.76,   
    'music/momoe/043-走れ風と共に.mp3': 194.821224,
    'music/momoe/044-オレンジ・ブロッサム・ブルース.mp3': 295.183673,
    'music/momoe/045-初恋草紙.mp3': 228.91102,
    'music/momoe/046-モノトーンの肖像画.mp3': 241.031837,
    'music/momoe/047-歌い継がれてゆく歌のように.mp3': 298.370612,
    'music/momoe/048-夢先案内人.mp3': 246.047347,
    'music/momoe/049-I_CAME_FROM_横須賀.mp3': 225.697959,
    'music/momoe/050-イミテイション・ゴールド.mp3': 203.180408,
    'music/momoe/051-鏡の中のある日.mp3': 269.714286,
    'music/momoe/052-愛のTWILIGHT_TIME.mp3': 188.238367,
    'music/momoe/053-秋桜(コスモス).mp3': 216.189388,
    'music/momoe/054-最後の頁.mp3': 256.444082,
    'music/momoe/055-寒椿.mp3': 266.161633,
    'music/momoe/056-青い羊歯(しだ)~アじアンタム.mp3': 267.232653,
    'music/momoe/057-赤い絆~レッド・センセーション.mp3': 251.794286,
    'music/momoe/058-口約束.mp3': 242.416327,
    'music/momoe/059-乙女座宮.mp3': 235.650612,
    'music/momoe/060-視線上のアリア.mp3': 218.174694,
    'music/momoe/061-プレイバックpart2.mp3': 202.187755,
    'music/momoe/062-ただよいの中で.mp3': 290.272653,
    'music/momoe/063-時の扉.mp3': 264.176327,
    'music/momoe/064-COSMOS(宇宙).mp3': 254.223673,
    'music/momoe/065-たそがれ祭り.mp3': 212.976327,
    'music/momoe/066-絶体絶命.mp3': 169.639184,
    'music/momoe/067-いい日旅立ち.mp3': 256.992653,
    'music/momoe/068-落葉の里.mp3': 218.462041,
    'music/momoe/069-スキャンダル~愛の日々.mp3': 245.942857,
    'music/momoe/070-霧雨楼.mp3': 241.580408,
    'music/momoe/071-ラスト・ソング.mp3': 379.742041,
    'music/momoe/072-曼珠沙華.mp3': 309.498776,
    'music/momoe/073-横須賀サンセット・サンライズ.mp3': 266.083265,
    'music/momoe/074-美・サイレント.mp3': 229.198367,
    'music/momoe/075-おだやかな構図.mp3': 245.942857,
    'music/momoe/076-想い出のミラージュ.mp3': 279.118367,
    'music/momoe/077-夜へ….mp3': 255.059592,
    'music/momoe/078-愛の嵐.mp3': 244.532245,
    'music/momoe/079-A_GOLD_NEEDLE_AND_SILVER_THREAD.mp3': 253.048163,
    'music/momoe/080-DANCIN’_IN_THE_RAIN.mp3': 340.114286,
    'music/momoe/081-CRY_FOR_ME.mp3': 273.188571,
    'music/momoe/082-しなやかに歌って.mp3': 290.507755,
    'music/momoe/083-娘たち.mp3': 296.254694,
    'music/momoe/084-愛染橋.mp3': 228.205714,
    'music/momoe/085-春爛漫.mp3': 220.630204,
    'music/momoe/086-あなたへの子守唄.mp3': 258.795102,
    'music/momoe/087-イントロダクション・春.mp3': 277.76,   
    'music/momoe/088-ロックンロール・ウィドウ.mp3': 241.240816,
    'music/momoe/089-アホカリプス・ラブ.mp3': 230.661224,
    'music/momoe/090-E=MC[↑]2.mp3': 275.983673,
    'music/momoe/091-さよならの向う側.mp3': 363.180408,
    'music/momoe/092-死と詩~death_and_poem.mp3': 203.937959,
    'music/momoe/093-不死鳥(フェニックス)伝説.mp3': 278.256327,
    'music/momoe/094-テレパシーナ.mp3': 318.432653,
    'music/momoe/095-This_is_my_trial~私の試練.mp3': 337.763265,
    'music/momoe/096-想い出のストロベリーフィールズ.mp3': 245.733878,
    'music/momoe/097-神様のおほし召し.mp3': 227.291429,
    'music/momoe/098-Crazy_Love.mp3': 289.802449,
    'music/momoe/099-一恵.mp3': 370.02449,
    'music/momoe/100-惜春(せきしゅん)通り.mp3': 193.227755,
}

MUSIC_NAME_LIST = [
    'music/momoe/001-としごろ.mp3',
    'music/momoe/002-叱らないでね.mp3',
    'music/momoe/003-ひとりぼっちのあなた.mp3',
    'music/momoe/004-青い果実.mp3',
    'music/momoe/005-おかしな恋人.mp3',
    'music/momoe/006-パパは恋人.mp3',
    'music/momoe/007-禁じられた遊び.mp3',
    'music/momoe/008-悩み多い14才.mp3',
    'music/momoe/009-春風のいたずら.mp3',
    'music/momoe/010-雨に濡れた少女.mp3',
    'music/momoe/011-15才の恋.mp3',
    'music/momoe/012-ひと夏の経験.mp3',
    'music/momoe/013-太陽の友達.mp3',
    'music/momoe/014-まばたきの夏.mp3',
    'music/momoe/015-教室を出たら大人.mp3',
    'music/momoe/016-ちっぽけな感傷.mp3',
    'music/momoe/017-清潔な恋.mp3',
    'music/momoe/018-冬の色.mp3',
    'music/momoe/019-伊豆の踊り子.mp3',
    'music/momoe/020-野菊の墓.mp3',
    'music/momoe/021-聖少女.mp3',
    'music/momoe/022-湖の決心.mp3',
    'music/momoe/023-春の奇蹟.mp3',
    'music/momoe/024-少年の海(出逢い).mp3',
    'music/momoe/025-美(み)え貝.mp3',
    'music/momoe/026-初恋時代.mp3',
    'music/momoe/027-夏ひらく青春.mp3',
    'music/momoe/028-ささやかな欲望.mp3',
    'music/momoe/029-ありがとうあなた.mp3',
    'music/momoe/030-白い約束.mp3',
    'music/momoe/031-山鳩.mp3',
    'music/momoe/032-空はこんなに青い.mp3',
    'music/momoe/033-愛に走って.mp3',
    'music/momoe/034-赤い運命.mp3',
    'music/momoe/035-木漏れ日.mp3',
    'music/momoe/036-碧色の瞳.mp3',
    'music/momoe/037-横須賀ストーリー.mp3',
    'music/momoe/038-GAME_IS_OVER.mp3',
    'music/momoe/039-陽炎(かげろう).mp3',
    'music/momoe/040-いま目覚めた子供のように.mp3',
    'music/momoe/041-パールカラーにゆれて.mp3',
    'music/momoe/042-赤い衝撃.mp3',
    'music/momoe/043-走れ風と共に.mp3',
    'music/momoe/044-オレンジ・ブロッサム・ブルース.mp3',
    'music/momoe/045-初恋草紙.mp3',
    'music/momoe/046-モノトーンの肖像画.mp3',
    'music/momoe/047-歌い継がれてゆく歌のように.mp3',
    'music/momoe/048-夢先案内人.mp3',
    'music/momoe/049-I_CAME_FROM_横須賀.mp3',
    'music/momoe/050-イミテイション・ゴールド.mp3',
    'music/momoe/051-鏡の中のある日.mp3',
    'music/momoe/052-愛のTWILIGHT_TIME.mp3',
    'music/momoe/053-秋桜(コスモス).mp3',
    'music/momoe/054-最後の頁.mp3',
    'music/momoe/055-寒椿.mp3',
    'music/momoe/056-青い羊歯(しだ)~アじアンタム.mp3',
    'music/momoe/057-赤い絆~レッド・センセーション.mp3',
    'music/momoe/058-口約束.mp3',
    'music/momoe/059-乙女座宮.mp3',
    'music/momoe/060-視線上のアリア.mp3',
    'music/momoe/061-プレイバックpart2.mp3',
    'music/momoe/062-ただよいの中で.mp3',
    'music/momoe/063-時の扉.mp3',
    'music/momoe/064-COSMOS(宇宙).mp3',
    'music/momoe/065-たそがれ祭り.mp3',
    'music/momoe/066-絶体絶命.mp3',
    'music/momoe/067-いい日旅立ち.mp3',
    'music/momoe/068-落葉の里.mp3',
    'music/momoe/069-スキャンダル~愛の日々.mp3',
    'music/momoe/070-霧雨楼.mp3',
    'music/momoe/071-ラスト・ソング.mp3',
    'music/momoe/072-曼珠沙華.mp3',
    'music/momoe/073-横須賀サンセット・サンライズ.mp3',
    'music/momoe/074-美・サイレント.mp3',
    'music/momoe/075-おだやかな構図.mp3',
    'music/momoe/076-想い出のミラージュ.mp3',
    'music/momoe/077-夜へ….mp3',
    'music/momoe/078-愛の嵐.mp3',
    'music/momoe/079-A_GOLD_NEEDLE_AND_SILVER_THREAD.mp3',
    'music/momoe/080-DANCIN’_IN_THE_RAIN.mp3',
    'music/momoe/081-CRY_FOR_ME.mp3',
    'music/momoe/082-しなやかに歌って.mp3',
    'music/momoe/083-娘たち.mp3',
    'music/momoe/084-愛染橋.mp3',
    'music/momoe/085-春爛漫.mp3',
    'music/momoe/086-あなたへの子守唄.mp3',
    'music/momoe/087-イントロダクション・春.mp3',
    'music/momoe/088-ロックンロール・ウィドウ.mp3',
    'music/momoe/089-アホカリプス・ラブ.mp3',
    'music/momoe/090-E=MC[↑]2.mp3',
    'music/momoe/091-さよならの向う側.mp3',
    'music/momoe/092-死と詩~death_and_poem.mp3',
    'music/momoe/093-不死鳥(フェニックス)伝説.mp3',
    'music/momoe/094-テレパシーナ.mp3',
    'music/momoe/095-This_is_my_trial~私の試練.mp3',
    'music/momoe/096-想い出のストロベリーフィールズ.mp3',
    'music/momoe/097-神様のおほし召し.mp3',
    'music/momoe/098-Crazy_Love.mp3',
    'music/momoe/099-一恵.mp3',
    'music/momoe/100-惜春(せきしゅん)通り.mp3',
    'music/momoe/101-輪廻.mp3',
    'music/momoe/102-あやつり人形館.mp3',
    'music/momoe/103-琥珀の季節.mp3',
    'music/momoe/104-闇の薫り.mp3',
    'music/momoe/105-Jigsaw_Puzzle.mp3',
    'music/momoe/106-幕間の風景.mp3',
    'music/momoe/107-恋は千里眼.mp3',
    'music/momoe/108-昨日までの顔.mp3',
    'music/momoe/109-野薔薇.mp3',
    'music/momoe/110-愛がひとつあれば.mp3',
    'music/momoe/111-感傷旅行.mp3',
    'music/momoe/112-感じる季節.mp3',
    'music/momoe/113-燃える海.mp3',
    'music/momoe/114-少女の誇り.mp3',
    'music/momoe/115-あなたが死んだら.mp3',
    'music/momoe/116-哀愁のコニーアイランド.mp3',
    'music/momoe/117-BLACK_CAB(ロンドン・タクシー).mp3',
    'music/momoe/118-序曲.mp3',
    'music/momoe/119-海から零へ.mp3',
    'music/momoe/120-MissBoy.mp3',
    'music/momoe/121-ブラックボール.mp3',
    'music/momoe/122-WHO.mp3',
    'music/momoe/123-スペース・トラブル危機一髪.mp3',
    'music/momoe/124-ダンシング・スターシャイン.mp3',
    'music/momoe/125-空から無限大.mp3',
    'music/momoe/126-謝肉祭.mp3',
]

MUSIC_TIME_LIST = [
    159.268571,#'001-としごろ.mp3',
    162.168163,#'002-叱らないでね.mp3',
    184.894694,#'003-ひとりぼっちのあなた.mp3',
    150.151837,#'004-青い果実.mp3',
    149.263673,#'005-おかしな恋人.mp3',
    165.433469,#'006-パパは恋人.mp3',
    182.909388,#'007-禁じられた遊び.mp3',
    145.789388,#'008-悩み多い14才.mp3',
    168.097959,#'009-春風のいたずら.mp3',
    190.92898, #'010-雨に濡れた少女.mp3',
    167.523265,#'011-15才の恋.mp3',
    159.111837,#'012-ひと夏の経験.mp3',
    191.164082,#'013-太陽の友達.mp3',
    147.043265,#'014-まばたきの夏.mp3',
    172.094694,#'015-教室を出たら大人.mp3',
    184.058776,#'016-ちっぽけな感傷.mp3',
    196.91102, #'017-清潔な恋.mp3',
    181.890612,#'018-冬の色.mp3',
    184.032653,#'019-伊豆の踊り子.mp3',
    169.822041,#'020-野菊の墓.mp3',
    221.152653,#'021-聖少女.mp3',
    197.250612,#'022-湖の決心.mp3',
    173.244082,#'023-春の奇蹟.mp3',
    216.137143,#'024-少年の海(出逢い).mp3',
    156.577959,#'025-美(み)え貝.mp3',
    169.560816,#'026-初恋時代.mp3',
    188.577959,#'027-夏ひらく青春.mp3',
    199.88898, #'028-ささやかな欲望.mp3',
    216.346122,#'029-ありがとうあなた.mp3',
    224.470204,#'030-白い約束.mp3',
    185.70449, #'031-山鳩.mp3',
    202.527347,#'032-空はこんなに青い.mp3',
    219.559184,#'033-愛に走って.mp3',
    192.078367,#'034-赤い運命.mp3',
    225.201633,#'035-木漏れ日.mp3',
    205.714286,#'036-碧色の瞳.mp3',
    232.306939,#'037-横須賀ストーリー.mp3',
    211.983673,#'038-GAME_IS_OVER.mp3',
    258.246531,#'039-陽炎(かげろう).mp3',
    234.945306,#'040-いま目覚めた子供のように.mp3',
    188.003265,#'041-パールカラーにゆれて.mp3',
    213.76,    #'042-赤い衝撃.mp3',
    194.821224,#'043-走れ風と共に.mp3',
    295.183673,#'044-オレンジ・ブロッサム・ブルース.mp3',
    228.91102, #'045-初恋草紙.mp3',
    241.031837,#'046-モノトーンの肖像画.mp3',
    298.370612,#'047-歌い継がれてゆく歌のように.mp3',
    246.047347,#'048-夢先案内人.mp3',
    225.697959,#'049-I_CAME_FROM_横須賀.mp3',
    203.180408,#'050-イミテイション・ゴールド.mp3',
    269.714286,#'051-鏡の中のある日.mp3',
    188.238367,#'052-愛のTWILIGHT_TIME.mp3',
    216.189388,#'053-秋桜(コスモス).mp3',
    256.444082,#'054-最後の頁.mp3',
    266.161633,#'055-寒椿.mp3',
    267.232653,#'056-青い羊歯(しだ)~アじアンタム.mp3',
    251.794286,#'057-赤い絆~レッド・センセーション.mp3',
    242.416327,#'058-口約束.mp3',
    235.650612,#'059-乙女座宮.mp3',
    218.174694,#'060-視線上のアリア.mp3',
    202.187755,#'061-プレイバックpart2.mp3',
    290.272653,#'062-ただよいの中で.mp3',
    264.176327,#'063-時の扉.mp3',
    254.223673,#'064-COSMOS(宇宙).mp3',
    212.976327,#'065-たそがれ祭り.mp3',
    169.639184,#'066-絶体絶命.mp3',
    256.992653,#'067-いい日旅立ち.mp3',
    218.462041,#'068-落葉の里.mp3',
    245.942857,#'069-スキャンダル~愛の日々.mp3',
    241.580408,#'070-霧雨楼.mp3',
    379.742041,#'071-ラスト・ソング.mp3',
    309.498776,#'072-曼珠沙華.mp3',
    266.083265,#'073-横須賀サンセット・サンライズ.mp3',
    229.198367,#'074-美・サイレント.mp3',
    245.942857,#'075-おだやかな構図.mp3',
    279.118367,#'076-想い出のミラージュ.mp3',
    255.059592,#'077-夜へ….mp3',
    244.532245,#'078-愛の嵐.mp3',
    253.048163,#'079-A_GOLD_NEEDLE_AND_SILVER_THREAD.mp3',
    340.114286,#'080-DANCIN’_IN_THE_RAIN.mp3',
    273.188571,#'081-CRY_FOR_ME.mp3',
    290.507755,#'082-しなやかに歌って.mp3',
    296.254694,#'083-娘たち.mp3',
    228.205714,#'084-愛染橋.mp3',
    220.630204,#'085-春爛漫.mp3',
    258.795102,#'086-あなたへの子守唄.mp3',
    277.76,    #'087-イントロダクション・春.mp3',
    241.240816,#'088-ロックンロール・ウィドウ.mp3',
    230.661224,#'089-アホカリプス・ラブ.mp3',
    275.983673,#'090-E=MC[↑]2.mp3',
    363.180408,#'091-さよならの向う側.mp3',
    203.937959,#'092-死と詩~death_and_poem.mp3',
    278.256327,#'093-不死鳥(フェニックス)伝説.mp3',
    318.432653,#'094-テレパシーナ.mp3',
    337.763265,#'095-This_is_my_trial~私の試練.mp3',
    245.733878,#'096-想い出のストロベリーフィールズ.mp3',
    227.291429,#'097-神様のおほし召し.mp3',
    289.802449,#'098-Crazy_Love.mp3',
    370.02449, #'099-一恵.mp3',
    193.227755,#'100-惜春(せきしゅん)通り.mp3',
    305.084082,#"101-輪廻.mp3"
    252.447347,#"102-あやつり人形館.mp3"
    277.368163,#"103-琥珀の季節.mp3"
    268.956735,#"104-闇の薫り.mp3"
    275.879184,#"105-Jigsaw_Puzzle.mp3"
    229.198367,#"106-幕間の風景.mp3"
    319.921633,#"107-恋は千里眼.mp3"
    186.313256,#"108-昨日までの顔.mp3"
    219.227567,#"109-野薔薇.mp3"
    192.034067,#"110-愛がひとつあれば.mp3"
    194.019378,#"111-感傷旅行.mp3"
    218.234938,#"112-感じる季節.mp3"
    197.441438,#"113-燃える海.mp3"
    183.074067,#"114-少女の誇り.mp3"
    190.257756,#"115-あなたが死んだら.mp3"
    261.172245,#"116-哀愁のコニーアイランド.mp3"
    266.370612,#"117-BLACK_CAB(ロンドン・タクシー)
    168.489796,#"118-序曲.mp3"
    328.960000,#"119-海から零へ.mp3"
    242.390204,#"120-Miss_Boy.mp3"
    280.711837,#"121-ブラックボール.mp3"
    336.274286,#"122-WHO.mp3"
    308.793469,#"123-スペース・トラブル危機一髪.mp
    241.057959,#"124-ダンシング・スターシャイン.mp
    147.017143,#"125-空から無限大.mp3"
    237.714286,#"126-謝肉祭.mp3"
]

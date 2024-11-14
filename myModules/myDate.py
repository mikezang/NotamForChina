from datetime import UTC, datetime, timedelta, timezone
from calendar import monthrange, month_abbr
import logging
from re import search
from time import localtime, strftime, time
from zoneinfo import ZoneInfo

from myModules import myConst
from myModules import myExcept

################################################################################################
def getJapanTimeFilename(fmt='') -> str:
    if fmt == '':
        fmt = "%Y%m%d-%H%M%S"
    return datetime.now(ZoneInfo(myConst.TIMEZONE_TOKYO)).strftime(fmt)

################################################################################################
def getJapanTime(fmt='') -> str:
    if fmt == '':
        fmt = "%Y/%m/%d %H:%M:%S"
    return datetime.now(ZoneInfo(myConst.TIMEZONE_TOKYO)).strftime(fmt)

################################################################################################
def getDDMM(ddmmss):
    ddmm = ''
    for ddmmssItem in ddmmss.split('-'):
        ddmm += '-' if ddmm != '' else ddmm
        if '|' in ddmmssItem:
            ddmmssList = ddmmssItem.split('|')
            ddmmList = [f'{dms[:7]},{dms[-11:-3]}' if len(dms.split('+')[0]) > 16 else dms for dms in ddmmssList]
            ddmm += '|'.join(ddmmList)
        else:
            plus = ddmmssItem.split('+')
            ddmm += f'{plus[0][:7]},{plus[0][-11:-3]}' if len(plus[0]) > 16 else plus[0]
            ddmm += '+' + plus[1] if len(plus) > 1 else ''
    return ddmm

################################################################################################
def convertMonthToNumber(month:str):
    monthDict = {month: f'{index:02d}' for index, month in enumerate(month_abbr) if month}
    return monthDict[month.capitalize()]

################################################################################################
def getLastdayOfMonth(year, month):
    return monthrange(int(year), int(month))[1]

################################################################################################
def getJapanTimeFilename(fmt='') -> str:
    if fmt == '':
        fmt = "%Y%m%d-%H%M%S"
    return datetime.now(ZoneInfo(myConst.TIMEZONE_TOKYO)).strftime(fmt)

################################################################################################
def getJapanTime(fmt='') -> str:
    if fmt == '':
        fmt = "%Y/%m/%d %H:%M:%S"
    return datetime.now(ZoneInfo(myConst.TIMEZONE_TOKYO)).strftime(fmt)

################################################################################################
def getThisYear():
    return getJapanDate()[:4]

################################################################################################
def getChinaTimeFromLocal(year, month, day):
    return datetime(year, month, day, tzinfo=ZoneInfo(myConst.TIMEZONE_SHANGHAI))

################################################################################################
def getUTCFromLocal(year, month, day):
    return datetime(year, month, day, tzinfo=ZoneInfo(myConst.TIMEZONE_SHANGHAI)).astimezone(timezone.utc)

################################################################################################
def getUTCFromChina(year, month, day):
    return datetime(year, month, day, tzinfo=timezone.utc)

################################################################################################
def getChinaTime(d, fmt=None):
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)

    if fmt:
        return d.astimezone(ZoneInfo(myConst.TIMEZONE_SHANGHAI)).strftime(fmt)
    else:
        return d.astimezone(ZoneInfo(myConst.TIMEZONE_SHANGHAI))

################################################################################################
def getJapanDate(fmt='') -> str:
    if fmt == '':
        fmt = "%Y%m%d"
    return datetime.now(ZoneInfo(myConst.TIMEZONE_TOKYO)).strftime(fmt)

################################################################################################
def setStartTime():
    global startTime
    startTime = time()
    
################################################################################################
def showRunTime():
    global startTime
    endTime = time()
    runTime = endTime - startTime
    print(f"\nFinish: {strftime('%Y-%m-%d %H:%M:%S', localtime(endTime))}")
    print(f'Run time: {timedelta(seconds=runTime)}')

################################################################################################
def convertTime(time1, start=True):
    if start:
        t = '00:00' if not time1 else f'{time1[:2]}:{time1[2:]}'
    else:
        t = '23:59' if not time1 else f'{time1[:2]}:{time1[2:]}'
    return t

################################################################################################
def convertDate(oldDate) -> str:
    for pattern, fmt in myConst.FORMAT_DATE.items():
        if search(pattern, oldDate):
            return datetime.strptime(oldDate, fmt).strftime("%Y/%m/%d %H:%M")
    return oldDate

################################################################################################
def convertToLocalDate(utcDate, tz, isLocalTime=False):
    if not isLocalTime:
        utcDate1 = datetime.strptime(utcDate, "%Y/%m/%d %H:%M").replace(tzinfo=UTC)
    else:
        utcDate1 = datetime.strptime(utcDate, "%Y/%m/%d %H:%M").replace(tzinfo=ZoneInfo(tz))
    return utcDate1.astimezone(ZoneInfo(tz))

################################################################################################
def convertToDate(d: str):
    from dateutil import parser
    try:
        if len(d) == 4:
            d = f'{d}0101'
        elif len(d) == 6:
            d = f'{d}01'
        return parser.parse(d)
    except:
        myExcept.printExceptionTrace() 

################################################################################################
def setLogging(filename):
    level = logging.INFO
    datefmt = "%Y-%m-%d %H:%M:%S"
    format = '%(asctime)s %(levelname)-6s %(processName)s %(name)s %(message)s'
    handlers = [logging.FileHandler(filename, encoding='utf-8'), logging.StreamHandler()]
    logging.basicConfig(level=level, handlers=handlers, encoding='utf-8', format=format, datefmt=datefmt)
    # logging.basicConfig(level=level, filename=filename, encoding='utf-8', format=format, datefmt=datefmt)
    # formatter = logging.Formatter(format)
    # console = logging.StreamHandler()
    # console.setLevel(logging.INFO)
    # console.setFormatter(formatter)
    # logging.getLogger().addHandler(console)

################################################################################################
def lenFullWidth(str):
    count = 0
    for char in str:
        count += 2 if ord(char) > 255 else 1
    return count




################################################################################################
import configparser
from datetime import datetime
from glob import glob
from re import findall

from matplotlib.dates import relativedelta

################################################################################################
def listFilesByGlob(partOfFilename):
    return [l.replace('\\', '/') for l in glob(partOfFilename)]

def openConfig(section=None) -> tuple:
    config_ini = configparser.ConfigParser()
    config_ini.read('config.ini', encoding='utf-8')
    if section is None:
        section = 'DEFAULT'
    readSection = config_ini[section]
    return readSection

################################################################################################
def readConfig(keys=None, returnList=True) -> tuple:
    read_default = openConfig()
    values = []

    if keys is None:
        from myModules import myDate
        values.append(read_default.get('ExcelFile'))
        # values.append(read_default.get('SheetLaunch'))
        values.append(read_default.get('Years'))
        rockets = []
        rockets.append(read_default.get('RocketsCZ'))
        rockets.append(read_default.get('RocketsNCZ'))
        rockets.append(read_default.get('Rockets'))
        values.append(rockets)
        retired = []
        retired.append(read_default.get('RetiredCZ'))
        retired.append(read_default.get('RetiredNCZ'))
        retired.append(read_default.get('Retired'))
        retired.append(read_default.get('RetiredDate'))
        values.append(retired)
        series = []
        series.append(read_default.get('SeriesCZ'))
        series.append(read_default.get('SeriesNCZ'))
        series.append(read_default.get('SeriesCZRockets'))
        series.append(read_default.get('SeriesNCZRockets'))
        series.append(read_default.get('Series'))
        values.append(series)
        values.append(read_default.get('Privates'))
        values.append(read_default.get('Locations'))
        values.append(myDate.getThisYear() + ',' + read_default.get('Categories'))
        taikonauts = read_default.get('Taikonauts')
        taikonauts = taikonauts.replace('()', f'({getSomeMonthAgo(1)})', 1)
        taikonauts = taikonauts.replace('()', f'({getSomeMonthAgo(3)})', 1)
        values.append(taikonauts)
        values.append(read_default.get('Payloads'))
        return values
    else:
        keys = [keys] if isinstance(keys, str) else keys
        if returnList:
            valueList = []
            for key in keys:
                values = read_default.get(key)
                for value in values.split(','):
                    valueList.append(value)
            return valueList
        else:
            values = ''
            for key in keys:
                values += read_default.get(key)
            return values

def getSomeMonthAgo(monthsAgo, format='%Y年%m月%d日'):
    current_date = datetime.now()
    past_date = current_date - relativedelta(months=monthsAgo)
    return past_date.strftime(format)

################################################################################################
def readConfigSpringFestival(year=None) -> str:
    section = openConfig()
    springFestivals = section.get('SpringFestival').split(',')
    springFestivals = [x for x in springFestivals if year in x]
    return springFestivals
################################################################################################
def readConfigFirNames() -> str:
    section = openConfig()
    count = int(section.get('FirCount'))
    firNames = ''
    for i in range(count):
        firName = section.get(f'FirName{i + 1}').replace(' ', '')
        firName = ' '.join([x.split('~')[0].split('+')[0] for x in firName.split(',')])
        if firNames:
            firNames += ' '
        firNames += firName
    return firNames

################################################################################################
def readConfigFirNamesDict() -> dict:
    section = openConfig()
    count = int(section.get('FirCount'))
    firNameDict = {}
    for i in range(count):
        firName = section.get(f'FirName{i + 1}').replace(' ', '')
        firName1 = ','.join([x.split('~')[0].split('+')[0] for x in firName.split(',')])
        firLaunchCenter = section.get(f'firLaunchCenter{i + 1}').replace(' ', '')
        firCondition = section.get(f'firCondition{i + 1}')
        firNameDict[i + 1] = (f'{firName}|{firName1}|{firLaunchCenter}|{firCondition}')
    return firNameDict

################################################################################################
def readConfigLaunchCenters() -> dict:
    firNames = ''
    firLaunchCenters = ''
    section = openConfig()
    count = int(section.get('FirCount'))
    for i in range(count):
        firName1 = section.get(f'FirName{i + 1}')
        firNames += ','.join([x.split('~')[0].split('+')[0] for x in firName1.split(',')]) + ','
        firLaunchCenters += section.get(f'FirLaunchCenter{i + 1}') + ','
    firNames = firNames.lstrip(',').replace(' ', '')
    firLaunchCenters = firLaunchCenters.lstrip(',').replace(' ', '')
    launchCenters = (dict(zip(firNames.split(','), firLaunchCenters.split(','))))
    return launchCenters

################################################################################################
def readConfigLocations():
    kmlFolders = {}
    locations = readConfig('Locations')
    for loc in locations:
        kmlFolders[loc] = readConfig(loc)[0]
    return kmlFolders

################################################################################################
def readConfigRetiredDict():
    retiredRockets = list(map(str.strip, readConfig('Retired')))
    retiredDates = list(map(str.strip, readConfig('RetiredDate')))
    retiredDict = dict(zip(retiredRockets, retiredDates))
    return retiredDict

################################################################################################
def readConfigSeriesDictList():
    czList = readConfig('SeriesCZ')
    nczList = readConfig('SeriesNCZ')
    czRocketList = readConfig('SeriesCZRockets')
    nczRocketList = readConfig('SeriesNCZRockets')
    seriesList = []
    for cz, czRocket in zip(czList, czRocketList):
        czRockets = czRocket.split('+')
        seriesDict = {}
        for rocket in czRockets:
            seriesDict[rocket] = f'{cz}系列'
        seriesList.append(seriesDict)
    for ncz, nczRocket in zip(nczList, nczRocketList):
        nczRockets = nczRocket.split('+')
        seriesDict = {}
        for rocket in nczRockets:
            seriesDict[rocket] = f'{ncz}系列'
        seriesList.append(seriesDict)
    return seriesList

################################################################################################
def readConfigMergeDict() -> dict:
    from myModules import myDate
    mergeDict = {}
    thisYear = myDate.getThisYear()
    section = openConfig()
    mergePath = section.get('MergeListPath')
    mergeListCount = int(section.get('mergeListCount'))

    for i in range(1, mergeListCount + 1):
        filename = section.get(f'MergeFilename{i}')
        image1PatternList = section.get(f'MergeList{i}').replace('{year}', thisYear).split('\n')
        image1List = []
        for line in image1PatternList:
            if line.endswith('??.png'):
                tempList = listFilesByGlob(line) + listFilesByGlob(line.replace('??.png', '.png'))
                image1List.extend(sorted(tempList))
            elif line.endswith('?.png'):
                tempList = listFilesByGlob(line) + listFilesByGlob(line.replace('?.png', '.png'))
                image1List.extend(sorted(tempList))
            elif line.endswith('?.mp4'):
                tempList = listFilesByGlob(line) + listFilesByGlob(line.replace('?.mp4', '.mp4'))
                image1List.extend(sorted(tempList))
            else:
                image1List.append(line)

        mergeDict[mergePath + filename] = image1List
    return mergeDict

################################################################################################
def readConfigRockets():
    read_default = openConfig()
    rockets = read_default.get('Rockets').split(',')
    return rockets

################################################################################################
def getLocation(newFile):
    locations = readConfig(['Locations'], False)
    pattern = r'(' + locations.replace(',', '|') + ')'
    try:
        locs = findall(pattern, newFile.split('\\')[-1])
    except:
        pass
    if locs:
        if locs[0] == '文昌':
            locs.append('海南') 
        if locs[0] == '海南':
            locs.append('文昌') 
        return locs, locations
    return None, locations


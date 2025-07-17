from datetime import datetime, timedelta
from json import dumps, loads
from os import path
from myModules import myDate

################################################################################################
def sortDictByValue(d: dict) -> dict:
    return {k : v for k, v in sorted(d.items(), key=lambda x: splitNotam(x))}

################################################################################################
def splitNotam(item):
    items = item[1].split(';')
    d = -float(items[3].split('°')[0][1:])
    d = d if items[3][0] == 'N' else -d # sort latitude from higher to lower
    return (items[0], d, items[2], item[0])

################################################################################################
def sortDictByEndDate(d: dict):
    sorted_tuples = sorted(d.items(), key=lambda item: item[1].split(";")[0][:10] + item[1].split(";")[1])
    sorted_dict = {k: v for k, v in sorted_tuples}
    return sorted_dict

################################################################################################
def sortDictByLatitude(d: dict):
    return {k : v for k, v in sorted(d.items(), key=lambda x: x[1])}

################################################################################################
def sortDictByKey(d: dict, reverse=False):
    return  {k : v for k, v in sorted(d.items(), key=lambda x: x[0], reverse=reverse)}

###############################################################################################
def printNotam(dictData, start=''):
    print(f"\nNOTAM发射预测{start}")
    print("================================")
    print(getNotamDictString(dictData))
    print("================================")
    print(f"NOTAM发射预测{start}\n")

################################################################################################
def isNewLaunch(oldDate, newDate, hours=2.0):
    dt1 = datetime.strptime(oldDate, '%Y/%m/%d %H:%M')
    dt2 = datetime.strptime(newDate, '%Y/%m/%d %H:%M')
    if dt2 - dt1 > timedelta(hours=hours):
        return True
    else:
        return False
    
################################################################################################
def getNotamDictString(d):
    msg = ''
    lastDate = ''
    i = 1
    j = 0
    for key, value in d.items():
        items = value.split(';')
        lastDate = items[0] if not lastDate  else lastDate
        if isNewLaunch(lastDate, items[0], 1.5):
            i += 1
            j = 1
            msg += '\n'
        else:
            j += 1
        msg += f'{i}{chr(j + 64)}: {items[2]},{key[-8:]},{items[0]},{items[1]};{myDate.getDDMM(items[3])}\n'
        lastDate = items[0]
    return msg[:-1]

################################################################################################
def printDict(d, withQuotation=False, hasNo=True):
    i = 1
    j = 1
    for i, (key, value) in enumerate(d.items()):
        no = f'{i + 1:02} ' if hasNo else ''
        item = f'{no}"{key}": "{value}"' if withQuotation else f'{no}{key}: {value}'
        print(item)

################################################################################################
def saveDictToTextFile(filename, dataDict):
    lines = ''
    with open(filename, 'w', encoding="utf-8") as f:
        for i, (key, value) in enumerate(dataDict.items(), 1):
            lines += f'{i:02} {key}: {value}\n'
        f.write(lines)
        print(f'Save dict to "{path.abspath(filename)}"')

################################################################################################
def saveDictToFile(filename: str, dataDict: dict):
    with open(filename, 'w', encoding="utf-8") as f:
        f.write(dumps(dataDict))
        print(f'Save dict to "{path.abspath(filename)}"')

################################################################################################
def readDictFromFile(filename: str):
    with open(filename) as f: 
        data = f.read()
        return loads(data) 
    

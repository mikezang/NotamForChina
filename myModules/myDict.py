from json import dumps, loads
from os import path
from myModules import myDate

################################################################################################
def sortDictByValue(d: dict) -> dict:
    return {k : v for k, v in sorted(d.items(), key=lambda x: splitNotam(x))}

################################################################################################
def splitNotam(item):
    items = item[1].split(';')
    return (items[0], items[1], -float(items[3].split('°')[0][1:]), items[2], item[0])

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
def getNotamDictString(d):
    msg = ''
    for i, (key, value) in enumerate(d.items()):
        items = value.split(';')
        msg += f'{i + 1:02}: {items[2]},{key[-8:]},{items[0]},{items[1]};{myDate.getDDMM(items[3])}\n'
    return msg[:-1]

################################################################################################
def printDict(d, withQuotation=False, hasNo=True):
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
    

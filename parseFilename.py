from datetime import timedelta
from timeit import timeit

from myModules import myFile
from myModules import myConfig

################################################################################################
def main():
    imageDict = myConfig.readConfigMergeDict("MERGE LIST")

    for mergePath, newList in imageDict.items():
        oldList, sharpLines = myFile.readTextFile(mergePath, True)
        if newList != oldList:
            # print(f'Old List: {oldList = }\n')
            # print(f'New List: {newList = }\n')
            oldItemList = [x for x in oldList if x not in newList]
            newItemList = [x for x in newList if x not in oldList]

            if oldItemList:
                print(f'Keep file {mergePath}!')
                print('  Old file not in folder:')
                for v in oldItemList:
                    print(f'    {v}')
                    
            if newItemList:
                myFile.saveTextFile(mergePath, '\n'.join(sharpLines + newList))
                print(f'  New File in folder:')
                for v in newItemList:
                    print(f'    {v}')
        else:
            print(f'Keep file {mergePath}!')

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'Finished in {timedelta(seconds=result)}\n')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")

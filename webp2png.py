"""
  Module: Convert webp to pn format.
  Author: ZANG Zhengrong
  Date: 2024/11/03
"""
from datetime import timedelta
from glob import glob
from sys import argv
from timeit import timeit
from PIL import Image

FILE_PATH = '\\Users\\w802479\\Downloads\\'

def webp2png(inputPath):
    try:
        with Image.open(inputPath) as img:
            outputPath = inputPath.replace('.webp', '.png')
            img.save(outputPath, 'PNG')
            print(f"Converted to {outputPath}")
    except:
        # print(f"An error occurred: {e}")
        pass

###############################################################################
def showUsage():
    print('Convert webp image to png format')
    print(f'{argv[0]} imagefilename')
    print('  imageFilename: filename without extension .webp')

###############################################################################
def main():
    if len(argv) == 1:
        showUsage()
    else:
        filename = argv[1] if argv[1].endswith('.webp') else argv[1] + '.webp'
        fileList = glob(filename)
        if not fileList and '\\' not in filename:
           filename = FILE_PATH + filename 
           fileList = glob(filename)

        if fileList:
            for imageFile in fileList:
                webp2png(imageFile)
        else:
            print(f'Not found any files: {filename}')

###############################################################################
def showRunTime(func):
   result = timeit(func, number=1, globals=globals())
   print(f'\nFinished in {timedelta(seconds=result)}')

if __name__ == '__main__':
   showRunTime('main()')

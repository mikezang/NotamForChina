from datetime import timedelta
from sys import argv
from timeit import timeit
from PIL import Image, ImageDraw, ImageFont

from myModules import myFile
from myModules import myDate

################################################################################################
def getFontPath():
    # Set the Chinese font
    if myFile.isWindows():
        font_path = 'C:/Windows/Fonts/simhei.ttf'
        font_path = 'C:/Windows/Fonts/simkai.ttf'
    elif myFile.isLinux():
        font_path = '//usr//share//fonts//truetype//wqy//wqy-microhei.ttc'
    elif myFile.isMacOS():
        font_path = '//usr//local//share//fonts//truetype//SimHei.ttf'
        font_path = '//usr//local//share//fonts//truetype//SimKai.ttf'
    return font_path

################################################################################################
def create_cover_image(text, fontPath='', fontSize=48, width=864, height=504, background_color="orange", text_color="black"):
    img = Image.new("RGB", (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    try:
        fontPath = getFontPath()
        font = ImageFont.truetype(fontPath, fontSize)
    except IOError:
        print("Font not found, using default font!")
        font = ImageFont.load_default()

    lines = text.split('\n')
    lines.append('　')
    # lines.append('　')
    lines.append('创作者：峥嵘不藏　')
    lines.append(f'创作日：{myDate.getJapanDate('%Y/%m/%d')}')
    line_height = draw.textbbox((0, 0), lines[0], font=font)[3]
    total_text_height = len(lines) * line_height
    text_y = (height - total_text_height) // 4

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, text_y), line, font=font, fill=text_color)
        text_y += line_height if i == len(lines) - 2 else line_height * 2

    img.save("images/cover.png")

################################################################################################
def main():
    if len(argv) > 1:
        date = argv[1]    
        if len(argv[1]) == 8:
            date = f'{date[:4]}年{date[4:6]}月{date[6:8]}日'
    else:
        date = myDate.getJapanDate('%Y年%m月%d日')

    text = f"{date}\n中国运载火箭发射统计"
    text = f'截止{text}' if not text.startswith('截止') else text
    print(f'Create Cover as below:\n{text}')
    create_cover_image(text, background_color="orange")

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")
    exit

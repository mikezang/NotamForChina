import calendar
from datetime import datetime, timedelta
import os
from sys import argv
from timeit import timeit

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm

from myModules import myConfig, myExcel

#######################################################################################################################
def parseLaunches(year, month, dfMotnh):
    launchMap = {}
    realLaunches = 0
    success = 0
    now = datetime.now()

    dfMotnh = dfMotnh.rename(columns={
        myExcel.EXCEL_COLUMN_DATE: 'date', myExcel.EXCEL_COLUMN_TIME: 'time', myExcel.EXCEL_COLUMN_PAYLOAD: 'payload',
        myExcel.EXCEL_COLUMN_LOCATION: 'location', myExcel.EXCEL_COLUMN_RESULT: 'result', myExcel.EXCEL_COLUMN_SPOT: 'spot', 
        myExcel.EXCEL_COLUMN_ROCKET: 'rocket', myExcel.EXCEL_COLUMN_NUMBER: 'yao', myExcel.EXCEL_COLUMN_REMARKS: 'remark'}
    )

    for row in dfMotnh.itertuples(index=False):
        dt = row.date

        if dt.year != year or dt.month != month:
            continue

        if row.time != '':
            hour, minute = map(int, row.time[:5].split('时'))
            dt = dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # if now > dt:
        if row.result != "":
            realLaunches += 1
            if row.result == "成功":
                success += 1
                ok = ''
            else:
                ok = 'X'
        else:
            ok = "?"

        text = '约'if ok == '?' else ''
        text += f"{row.time[:6]}"
        text += f"{row.spot.split('(')[0]}" if row.location == '海上' else f"{row.location}"
        text += f"\n{ok}{row.rocket}{row.yao}"
        text += '\n' + row.remark if row.remark else ''
        launchMap.setdefault(dt.day, []).append(text)

    rate = f'{float(success / realLaunches):.02%}' if realLaunches > 0 else "-"
    return launchMap, realLaunches, success, rate

#######################################################################################################################
def plotLaunchCalendar(year, month, dfLaunches, saveFile=None, title=None, isShow=True):
    launchMap = {}
    calendar.setfirstweekday(calendar.SUNDAY)
    weeks = calendar.monthcalendar(year, month)
    today = datetime.today().date()

    if not title:
        title = f"{year}年{month:02d}月中国运载火箭发射日历"

    dfMotnh = dfLaunches[(dfLaunches[myExcel.EXCEL_COLUMN_DATE].dt.year == year) & (dfLaunches[myExcel.EXCEL_COLUMN_DATE].dt.month == month)]
    if len(dfMotnh) == 0:
        return
    
    launchMap, realLaunches, success, rate = parseLaunches(year, month, dfMotnh)
    fig, ax = plt.subplots(figsize=(11.69, 8.27))

    rows = len(weeks) 
    summaryHeight = 0.4
    ax.set_xlim(0, 7)
    ax.set_ylim(rows + summaryHeight, -1)
    ax.axis("off")

    weekNames = ["日", "一", "二", "三", "四", "五", "六"]

    for i, name in enumerate(weekNames):
        ax.text(i + 0.5, -0.2, name, fontsize=20, ha="center", color="red" if i in [0, 6] else "black")

    for row, week in enumerate(weeks):
        for col, day in enumerate(week):
            bg = "white" 

            if col in [0, 6]:
                bg = "#FFCCF7"

            if day in launchMap:
                bg = "#FFF7CC"

            ax.add_patch(Rectangle((col, row), 1, 1, facecolor=bg, edgecolor="black", linewidth=1.5))

            if day == 0:
                continue

            dayStr = f'{day} 今日' if today.day == day and today.month == month and today.year == year else str(day)
            ax.text(col + 0.03, row + 0.05, dayStr, fontsize=18, ha="left", va="top", color="red" if col in [0, 6] else "black")

            if day in launchMap:
                items = launchMap[day]
                launchText = "\n\n".join(f"{x}" for x in items)
                fontSize = 10 if len(launchText.split('\n')) < 6 else 9 if len(launchText.split('\n')) < 7 else 8
                drow = 0.32 if len(launchText.split('\n')) < 4 else 0.27 if len(launchText.split('\n')) < 6 else 0.22
                drow = drow if len(launchText.split('\n\n')) < 3 else 0.20
                ax.text(col + 0.05, row + drow, launchText, fontsize=fontSize, ha="left", va="top", wrap=True)

    predic = f"预测发射数：{len(dfMotnh)}"
    sammary = f"发射数：{int(realLaunches)}  成功数：{int(success)}  成功率：{rate}"
    ax.text(3.5, -0.85, title, fontsize=30, ha="center", va="center")

    if today.year <= year and today.month <= month:
        ax.text(4.1, rows + 0.25, predic, fontsize=16, ha="left", va="center")
    ax.text(0.1, rows + 0.25, sammary, fontsize=16, ha="left", va="center")

    plt.subplots_adjust(top=0.98, bottom=0.05, left=0.03, right=0.97)

    if saveFile:
        print(f'Save to {saveFile}')
        plt.savefig(saveFile, dpi=300, bbox_inches="tight")

    if isShow:
        plt.show()

    plt.close(fig)

def main():
    folder = 'calendar'
    os.makedirs(folder, exist_ok=True)
    EXCEL_FILE = myConfig.readConfig('ExcelFile', False)
    SHEET_LAUNCH = myConfig.readConfig('SheetLaunch', False)
    dfLaunches = myExcel.parseExcelSheetLaunch(EXCEL_FILE, SHEET_LAUNCH, withPredict=True)

    fontPath = './fonts/simkai.ttf'
    fm.fontManager.addfont(fontPath)
    cn_font = fm.FontProperties(fname=fontPath)
    plt.rcParams['font.family'] = cn_font.get_name()
    plt.rcParams['axes.unicode_minus'] = False

    if len(argv) > 1:
        if argv[1] == 'all':
            for year in range(1970, datetime.today().year + 1):
                for month in range(1, 13):
                    title = f"{year}年{month:02d}月中国运载火箭发射日历"
                    plotLaunchCalendar(year, month, dfLaunches, saveFile=f"{folder}/{year}{month:02d}.png", title=title, isShow=False)
            return
        elif len(argv[1]) == 6:
            year = int(argv[1][:4])
            month = int(argv[1][4:])
    else:
        today = datetime.today().date()
        year = today.year
        month = today.month

    title = f"{year}年{month:02d}月中国运载火箭发射日历"
    plotLaunchCalendar(year, month, dfLaunches, saveFile=f"{folder}/{year}{month:02d}.png", title=title)

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}\n')
    
if __name__ == "__main__":
    showRunTime("main()")
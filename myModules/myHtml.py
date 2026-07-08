from myModules import myDate
from myModules import myConfig

# City,Tint,Vividness,Brightness,Red,Green,Blue
# 酒泉,16,201,177,244,176,132,
# 西昌,64,99,165,169,208,142
# 太原,30,240,168,255,217,102
# 文昌,139,142,201,189,215,238
# 海上,139,141,107,47,117,181
# 海南,146,124,170,142,169,219
# 成功,64,101,86,84,130,53
F_Tint = 0.075
F_Vivid = 0.035
F_Bright = 0.15

CITY_MAPPING = {
    '酒泉': 'jiuquan',
    '西昌': 'xichang',
    '太原': 'taiyuan',
    '文昌': 'wenchang',
    '海上': 'haishang',
    '东海': 'haishang',
    '黄海': 'haishang',
    '南海': 'haishang',
    '海南': 'hainan',
    '成功': 'ok',
    '部分<BR>成功': 'part',
    '部分成功': 'part',
    '失败': 'ng',
    }
# CityColorsOnly = [
#     {"City":'酒泉jiuquan', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 244, "Green": 176, "Blue": 132},
#     {"City":'西昌xichang', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 169, "Green": 208, "Blue": 142},
#     {"City":'太原taiyuan', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 255, "Green": 217, "Blue": 102},
#     {"City":'文昌wenchang', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 189, "Green": 215, "Blue": 238},
#     {"City":'海上haishang', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 47, "Green": 117, "Blue": 181},
#     {"City":'海南hainan', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 142, "Green": 169, "Blue": 219},
#     {"City":'成功ok', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 84, "Green": 130, "Blue": 53},
#     {"City":'失败ng', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 255, "Green": 0, "Blue": 0},
#     {"City":'部分成功part', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 255, "Green": 153, "Blue": 0},
# ]

# CityColors = [
#     {"City":'酒泉Jiuquan', "Tint": 16, "Vivid": 201, "Bright": 177, "Red": 244, "Green": 176, "Blue": 132},
#     {"City":'西昌Xichang', "Tint": 64, "Vivid": 99, "Bright": 165, "Red": 169, "Green": 208, "Blue": 142},
#     {"City":'太原Taiyuan', "Tint": 30, "Vivid": 240, "Bright": 168, "Red": 255, "Green": 217, "Blue": 102},
#     {"City":'文昌Wenchang', "Tint": 139, "Vivid": 142, "Bright": 201, "Red": 189, "Green": 215, "Blue": 238},
#     {"City":'海上Haishang', "Tint": 139, "Vivid": 141, "Bright": 107, "Red": 47, "Green": 117, "Blue": 181},
#     {"City":'海南Hainan', "Tint": 146, "Vivid": 124, "Bright": 170, "Red": 142, "Green": 169, "Blue": 219},
# ]

################################################################################################
def createHtmlTable(dfList, title, iouList=None, iamgeList=None, retiredRockets=None, dfMatchTime=None, isLunarNewYear=False, isFirstLast=False, isMaiden=False):
    dfList = [dfList[key] for key in sorted(dfList.keys())] if isinstance(dfList, dict) else dfList
    title += f'（截止{myDate.getJapanTime("%Y年%m月%d日")}）'
    title = title.replace('春节', '春节前后') if '春节' in title else title

    html = buildHtmlBegin(title)

    if isLunarNewYear:
        headers = ['本页<BR>发射<BR>次数', '全部<BR>发射<BR>次数', '长征<BR>发射<BR>次数', '其他<BR>发射<BR>次数', '日期', '日差', '北京时间', '轨道', '结果', '发射地<BR>发射船', '运载火箭', '载荷']
        textAligns = ['', '', '', '', '', '', '', 'left', '', '', 'left', 'left']
        widths = ['', '', '', '', '', '', '', '', '', '', '', '']
        nowraps = ['nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', '']
    elif isFirstLast or isMaiden:
        headers = ['本页<BR>发射<BR>次数', '全部<BR>发射<BR>次数', '长征<BR>发射<BR>次数', '其他<BR>发射<BR>次数', '日期', '北京时间', '轨道', '结果', '发射地<BR>发射船', '运载火箭', '载荷']
        textAligns = ['', '', '', '', '', '', 'left', '', '', 'left', 'left']
        widths = ['', '', '', '', '', '', '', '', '', '', '']
        nowraps = ['nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', '']
    else:
        headers = ['本页<BR>发射<BR>次数', '全部<BR>发射<BR>次数', '长征<BR>发射<BR>次数', '其他<BR>发射<BR>次数', '日期', '北京时间', '轨道', '结果', '发射地<BR>发射船']
        headers += ['同地<BR>相隔<BR>日数', '同箭<BR>相隔<BR>日数', '运载火箭']
        headers += ['落区重叠率'] if iouList else []
        headers += ['预测发射时间'] if dfMatchTime else []
        headers += ['载荷']

        textAligns = ['', '', '', '', '', '', 'left', '', '', '', '', 'left']
        textAligns += ['right'] if iouList else []
        textAligns += ['center'] if dfMatchTime else []
        textAligns += ['left']

        widths = ['', '', '', '', '', '', '', '', '', '', '', '']
        widths += [''] if iouList else []
        widths += [''] if dfMatchTime else []
        widths += ['']

        nowraps = ['nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap', 'nowrap']
        nowraps += ['nowrap'] if iouList else []
        nowraps += ['nowrap'] if dfMatchTime else []
        nowraps += ['']

    for i, df in enumerate(dfList):
        dfCopy = df.copy()

        if isLunarNewYear:
            dfCopy['year'] = dfCopy['日期'].dt.year
            springFestival = (
                dfCopy.loc[dfCopy['火箭'] == '春节', ['year', '日期']]
                .set_index('year')['日期']
            )
            dfCopy['春节日'] = dfCopy['year'].map(springFestival)
            dfCopy['日差'] = (dfCopy['日期'] - dfCopy['春节日']).dt.days

        titleNew = title.replace('（', str(i + 1) + '（') if len(dfList) > 1 else title

        html += buildTableBegin(titleNew, headers)
        firstYear = str(dfCopy.iloc[0]['日期'])[:4]
        lastYear = str(dfCopy.iloc[-1]['日期'])[:4]
        countChunjie = 0
        prevYear = None
        prevMonth = None

        for j, (_, row) in enumerate(dfCopy.iterrows()):
            year = str(row['日期'])[:4]
            month = str(row['日期'])[5:7]

            if row['火箭'] == '春节':
                countChunjie += 1

            if isLunarNewYear or isFirstLast or isMaiden:
                isNewRow = (prevYear != year)
            else:
                if firstYear == lastYear:
                    isNewRow = (prevYear != year) or (prevMonth != month)
                else:
                    isNewRow = (prevYear != year)

            index = i * 100 + j + 1 - countChunjie
            cells = buildRowCells(row, index, j, iouList, iamgeList, dfMatchTime, isLunarNewYear, isFirstLast, isMaiden)
            html += buildTableCell(cells, textAligns, widths, nowraps, retiredRockets, isNewRow=isNewRow)
            prevYear = year
            prevMonth = month
        html += buildTableEnd()

        if isMaiden:
            break
    html += buildHtmlEnd()
    return html

def buildRowCells(row, index, j, iouList=None, imageList=None, dfMatchTime=None, isLunarNewYear=False, isFirstLast=False, isMaiden=False):
    cells = []
    rocket = row['火箭']
    dateStr = str(row['日期'])
    date = f'{dateStr[:4]}年{dateStr[5:7]}月{dateStr[8:10]}日'
    location = row['地点']

    if rocket == '春节':
        cells.append('-')
        cells.append('-')
        cells.append('-')
        cells.append('-')
        cells.append(date)
        cells.append(location + rocket)
    else:
        allNo = row['总数']
        czNo = row['长征']
        nczNo = row['其他']
        time = row['时间\n（UTC+8）'][:6]
        arr = row['工位'].split('(')
        location = arr[0] + '<BR>' + arr[1].split('号')[0] + '号' if location == '海上' else location
        sameLocaionDays = int(row['同地相\n隔日数']) if row['同地相\n隔日数'] else '-'
        sameRocketDays = int(row['同箭相\n隔日数']) if row['同箭相\n隔日数'] else '首飞'
        result = row['结果']
        # result = f'{result[:2]}<BR>{result[2:]}' if len(result) > 2 else result
        orbit = row['轨道']
        xuhao = row['遥号']
        remark = row['备注']
        xuhao = f'{xuhao}<BR>{remark}' if hasUpperStage(remark) else xuhao
        countFullWidth = myDate.lenFullWidth(rocket + xuhao)
        xuhao = xuhao + ' ' * (17 - countFullWidth)
        payloads = row['载荷']
        countFullWidth = myDate.lenFullWidth(orbit)
        orbit = orbit + ' ' * (8 - countFullWidth)
        cells.append(f'{index:03d}')
        cells.append(allNo)
        cells.append(czNo if czNo else '-')
        cells.append(nczNo if nczNo else '-')
        cells.append(date)
        if isLunarNewYear:
            diff = int(row['日差'])
            DaysDiff = f'{abs(diff)}日'
            DaysDiff += '前' if diff < 0 else '后'
            cells.append(DaysDiff)
        cells.append(time)
        cells.append(orbit)
        cells.append(result)
        cells.append(location)
        if not isLunarNewYear and not isFirstLast and not isMaiden:
            cells.append(sameLocaionDays)
            cells.append(sameRocketDays)
        cells.append(f'{rocket}{xuhao}')
        if iouList:
            aText = '<BR>'.join(iouList[j]).replace('  MSA', '　MSA')
            aTag = f"<a href=javascript:void(0) onclick=openPopup('{imageList[j]}')>{aText}</a>"
            cells.append(aTag)
        if dfMatchTime:
            aText = '<BR>'.join(dfMatchTime[j])
            cells.append(aText)
        # if not isLunarNewYear and not isFirstLast:
        cells.append(payloads)

    return cells

################################################################################################
def printList(dfList, rocketPayload, singleRocket=False, onlyPrintYaoNumber=False):
    yaoMax = int(myConfig.readConfig(['最大遥号'])[0])
    yaoList = [i for i in range(1, yaoMax, 1)]
    yaoMax = 1
    dfList = [dfList[key] for key in sorted(dfList.keys())] if isinstance(dfList, dict) else dfList
    countChunjie = 0

    if not onlyPrintYaoNumber:
        print(f'\n{"*" * 50} Start of {rocketPayload} {"*" * 50}')

    for i, df in enumerate(dfList):
        for j, (_, row) in enumerate(df.iterrows()):
            index = i * 100 + j + 1 - countChunjie
            date = str(row['日期'])[:10]
            location = row['地点']
            rocket = row['火箭']

            if rocket != '春节':
                time = row['时间\n（UTC+8）'][:6].replace('时',':').replace('分','')
                xuhao = row['遥号']
                remark = row['备注']
                xuhao = f'{xuhao}/{remark}' if hasUpperStage(remark) else xuhao
                countFullWidth = myDate.lenFullWidth(rocket + xuhao)
                xuhao = xuhao + ' ' * (17 - countFullWidth)
                sameLocaionDays = int(row['同地相\n隔日数']) if row['同地相\n隔日数'] else '    '
                sameLocaionDays = str(sameLocaionDays).ljust(4)
                sameRocketDays = int(row['同箭相\n隔日数']) if row['同箭相\n隔日数'] else '    '
                sameRocketDays = str(sameRocketDays).ljust(4)
                result = row['结果']
                payloads = row['载荷']
                orbit = row['轨道'][:4]
                countFullWidth = myDate.lenFullWidth(orbit)
                orbit = orbit + ' ' * (8 - countFullWidth)
                if not onlyPrintYaoNumber:
                    print(f'{index:03d}: {date} {time} {result} {location} {sameLocaionDays} {sameRocketDays} {orbit} {rocket}{xuhao} {payloads}')
            else:
                countChunjie += 1
                print(f'     {date} {location}{rocket}')

            if singleRocket and rocketPayload and xuhao[0] == '遥':
                yaoHao = xuhao[1:].partition('/')[0]
                if int(yaoHao) in yaoList:
                    yaoList.remove(int(yaoHao))
                yaoMax = int(yaoHao) if int(yaoHao) > yaoMax else yaoMax
    if not onlyPrintYaoNumber:
        print(f'{"*" * 51} End of {rocketPayload} {"*" * 51}\n')

    if singleRocket and rocketPayload:
        if rocketPayload == '快舟一号甲':
            yaoMax = 33 if 33 > yaoMax else yaoMax
            yaoList.remove(33)
        yaoList = [i for i in yaoList if not (yaoMax < i <= 200)]
        yaoList.append(int(yaoMax + 1))
        # print(f'{rocketPayload}最大使用遥号： {yaoMax}')
        rocket = f'{rocketPayload.ljust(6, "　")}'
        print(f'{rocket}: {", ".join(map(str, yaoList))}, {yaoList[-1] + 1}, ...')

################################################################################################
def hasUpperStage(remark):
    return 'SD' in remark or 'SM' in remark or 'SMA' in remark or '遥' in remark

################################################################################################
def adjust_color(red, green, blue, tint=0, vivid=0, bright=0):
    """
    Adjusts the RGB values based on tint, vividness, and brightness.
    This is a simple adjustment for demonstration.
    """
    # Adjust the colors based on the tint, vividness, and brightness.
    # Scale the adjustments (these formulas can be customized)
    red =   min(255, max(0, int(- (255 - vivid) * F_Vivid + bright * F_Bright + tint * F_Tint + red)))
    green = min(255, max(0, int(- (255 - vivid) * F_Vivid + bright * F_Bright + tint * F_Tint + green )))
    blue =  min(255, max(0, int(- (255 - vivid) * F_Vivid + bright * F_Bright + tint * F_Tint + blue )))
    return red, green, blue

################################################################################################
# def getCityColorDict():
#     colorDict = {}
#     for color in CityColors:
#         city = color['City']
#         red = color['Red']
#         green = color['Green']
#         blue = color['Blue']
#         # tint = color['Tint']
#         # vivid = color['Vivid']
#         # bright = color['Bright']
#         colorDict[city] = (adjust_color(red, green, blue))
#     return colorDict

################################################################################################
def buildHtmlBegin(title):
    html = """<!DOCTYPE html>
    <HTML lang="en">
    <HEAD>
        <meta charset="UTF-8">
        <title>#title</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script>
            function saveTableAsImage(tableId) {
                const table = document.getElementById(tableId)
                html2canvas(table).then(canvas => {
                    //const date = new Date();
                    //const year = date.getFullYear();
                    //const month = String(date.getMonth() + 1).padStart(2, '0');
                    //const day = String(date.getDate()).padStart(2, '0');
                    //const hours = String(date.getHours()).padStart(2, '0');
                    //const minutes = String(date.getMinutes()).padStart(2, '0');
                    //const seconds = String(date.getSeconds()).padStart(2, '0');
                    //const localTime = `${year}${month}${day}-${hours}${minutes}${seconds}`;
                    const link = document.createElement('a');
                    link.href = canvas.toDataURL('image/png');
                    link.download = `${tableId}.png`;
                    //link.download = `${tableId}-${localTime}.png`;
                    link.click();
                });
            }
            let popupWindow = null;
            function openPopup(imgPath) {
                //if (popupWindow && !openWindow.closed) {
                //    popupWindow.focus();
                //    return;
                //}
                popupWindow = window.open("", "imgPath", "width=800,height=800,location=no");
                popupWindow.document.write(`
                    <html>
                    <head>
                        <title>Popup Image</title>
                        <style>
                            body {
                                margin: 0;
                                background: #000;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                height: 100%;
                            }
                            img {
                                max-width: 100%;
                                max-height: 100%;
                            }
                        </style>
                    </head>
                    <body>
                        <img src="` + imgPath + `" alt="` + imgPath + `" target=_blank>
                    </body>
                    </html>
                `);
            }
        </script>
        <style>
            body {
                font-family: 'KaiTi', 'KaiTi', '楷体', sans-serif;
                background-color: 'white';
            }
            pre {
                font-size: 16px;
            }
            .borderOnly {
                background-color: #F0F4F7;
            }
            .borderOnly th, .borderOnly td {
                text-align: center;
                font-size: 16px;
                vertical-align: middle;
                border: 1px solid black;
                padding-left: 1px;
                padding-right: 1px;
            }
            .border {
                border-collapse: collapse;
                width: 100%;
                border-top: 3px solid orange;
                border-bottom: 3px solid orange;
                border-left: 3px solid orange;
                border-right: 3px solid orange;
            }
            .border th, .border td {
                text-align: center;
                font-size: 16px;
                vertical-align: middle;
                border-left: 1px solid black;
                border-right: 1px solid black;
                border-top: 1px solid #ccc;
                border-bottom: 1px solid #ccc;
                padding: 2px 2px;
                position: relative;
            }
            .border tr.newRow th, .border tr.newRow td {
                text-align: center;
                font-size: 16px;
                vertical-align: middle;
                border-left: 1px solid black;
                border-right: 1px solid black;
                border-top: 2px solid orange;
                border-bottom: none;
                padding: 4px 2px;
                position: relative;
            }
            # .border tr.newRow th::before, .border tr.newRow td::before {
            #     content: "";
            #     position: absolute;
            #     left: 0;
            #     right: 0;
            #     top: 0;
            #     height: 2px;
            #     background: orange;
            # }
            # .border tr.newRow th::after, .border tr.newRow td::after {
            #     content: "";
            #     position: absolute;
            #     left: 0;
            #     right: 0;
            #     bottom: 0;
            #     height: 2px;
            #     background: orange;
            # }
            .no-border {
                border: none;
            }
            .no-border th, .no-border td {
                text-align: center;
                vertical-align: top;
            }
            button {
                color: blue;
                font-size: 20px;
            }
            .jiuquan {
                background-color: rgb(244,176,132);
            }
            .xichang {
                background-color: rgb(169,208,142);
            }
            .taiyuan {
                background-color: rgb(255,217,102);
            }
            .wenchang {
                background-color: rgb(189,215,238);
            }
            .haishang {
                background-color: rgb(47,117,181);
                color: white;
            }
            .hainan {
                background-color: rgb(142,169,219);
                color: white;
            }
            .retired {
                background-color: rgb(192,192,192);
            }
            .ok {
                background-color: rgb(84,130,53);
                color: white;
            }
            .ng {
                background-color: red;
                color: black;
            }
            .part {
                background-color: rgb(255,153,0);
                color: black;
            }
        </style>
    </HEAD>
    <HTML>
    <BODY>
        <CENTER><H1>#title</H1>
    """
    return html.replace('#title', title)

################################################################################################
def buildHtmlEnd():
    html = """
    </BODY>
    </HTML><BR><BR>
    """
    return html

################################################################################################
def buildTableBegin(tableId, headers, border=True):
    borderClass = 'border' if border else 'no-border'
    cols = len(headers)
    html = '<TABLE class=no-border><TR ><TH>\n'
    html += f'<button onclick=saveTableAsImage("{tableId}")>Save Table as {tableId}.png</button><BR>\n'
    html += '</TH></TR></TABLE>\n'
    html += f'<TABLE class=borderOnly><TR><TD>'
    html += f'<TABLE class={borderClass} id={tableId}>'
    html += f'<TR><TH colspan={cols}>{tableId}</TR></TH>\n'
    html += '<TR>'
    for th in headers:
       html += f'<TH nowrap>{th}</TH>'
    html += '</TR>\n'
    return html

################################################################################################
def buildTableEnd():
    html = "</TABLE></TD></TR></TABLE>\n"
    return html

################################################################################################
def getCityColor(colorDict, city):
    matches = next((key for key in colorDict if city in key))
    if matches:
        return (matches[2:], colorDict[matches])
    else:
        return ''

################################################################################################
def buildTableCell(cells, textAligns, widths, nowraps, retiredRockets=None, isNewRow=False):
    classTr = 'class=newRow' if isNewRow else ''
    tr = f'<TR {classTr}>'
    html = ''
    for cell, textAlign, width, nowrap in zip(cells, textAligns, widths, nowraps):
        textAlignStr = f'text-align: {textAlign}' if textAlign else ''
        widthStr = f'width: {width}' if width else ''
        styleStr = f'style="{textAlignStr}; {widthStr};"' if textAlign or width else ''
        classSrc = None

        if isinstance(cell, str):
            index1 = cell.find('遥')
            index2 = cell.find('天')
            rocket = cell[:index1] if index1 >= 0 else cell[index2] if index2 >= 0 else cell[:4]
            classSrc = f'class="retired"' if cell != '快舟一号卫星' and rocket in retiredRockets.keys() else ''
            locOrResult = cell[:2] if cell[1:2] == '海' else cell
            classSrc = f'class="{CITY_MAPPING.get(locOrResult)}"' if locOrResult in CITY_MAPPING.keys() else classSrc
        
        if cell == '中国春节':
            tr = f'<TR {classTr} style=background-color:pink>'
            html += f'<TD colspan=7 {classSrc} {nowrap} {styleStr}>{cell}</TD>'
        else:
            html += f'<TD {classSrc} {nowrap} {styleStr}>{cell}</TD>'
    html = tr + html + '</TR>\n'
    return html

###############################################################################
def createMenuPage(title):
    html = """
    <!DOCTYPE html>
    <html lang="en"
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width,  inital-scale=1.0">
        <title>#title</title>
        <style>
            body {
                margin: 0;
                font-fmaily: 'KaiTi', 'KaiTi', '楷体', sans-ferif;
            }
            .container {
                display: flex;
            }
            .menu {
                width: 50px;
                background-color: #F4F4F4;
                padding: 15px;
                box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
            }
            .menu h3 {
                cursor: pointer;
                padding: 5px;
                margin: 0;
                background: #ddd;
                border-radius: 3px;
            }
            .menu h3:hover {
                bacground: #ccc;
            }
            .submenu {
                display: none;
                padding-left: 15px;
            }
            .submenu a {
                display: block;
                margin: 5px 0;
                color: #333;
                text-decoration: none;
            }
            .submenu a:hover {
                text-decoration: underline;
            }
            .content {
                flex-grow: 1;
                padding: 15px;
            }
        </style>
        <script>
            // JavaScript function to toogle display of submenus
            function toogleMenu(event) {
                const nextElement = event.target.nextElementSibling;
                if (nextElement && nextElement.classList.contains('submenu')) {
                    nextElement.style.display = nextElement.style.display == 'block' ? 'none' : 'block';
                }
            }

            document.addEventListener('DOMContentLoader', () => {
                const categories = document.querySelectorAll('.menu h3');
                categories.forEach(category => {
                    category.addEventListener('click', toogleMenu);
                });
            });
        </script>
    </head>
    <body>
        <div class="container">
            <div class="menu">
                <h3>Category 1</h3>
                <div calss="submenu">
                    <a href="#">Item 1.1</a>
                    <a href="#">Item 1.2</a>
                    <a href="#">Item 1.3</a>
                    <a href="#">Item 1.4</a>
                </div>
                <h3>Category 2</h3>
                <div calss="submenu">
                    <a href="#">Item 2.1</a>
                    <a href="#">Item 2.2</a>
                </div>
                <h3>Category 3</h3>
                <div calss="submenu">
                    <a href="#">Item 3.1</a>
                    <a href="#">Item 3.2</a>
            </div>
            <div class="content">
                <h1>Welcome</h1>
                <p>This is the content area. You can add your page content here.</p>
            </div>
        </div>
    </body>
    </html>
    """
    html.replace('#title', title)
    with open("menu.html", "w", encoding="UTF-8") as file:
        file.write(html)
    print("menu.html created!")

###############################################################################
def main():
    createMenuPage("Test Menu")

###############################################################################
def showRunTime(func):
    from timeit import timeit
    from datetime import timedelta
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')

if __name__ == '__main__':
    showRunTime('main()')

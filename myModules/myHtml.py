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
    '失败': 'ng',
    }
CityColorsOnly = [
    {"City":'酒泉jiuquan', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 244, "Green": 176, "Blue": 132},
    {"City":'西昌xichang', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 169, "Green": 208, "Blue": 142},
    {"City":'太原taiyuan', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 255, "Green": 217, "Blue": 102},
    {"City":'文昌wenchang', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 189, "Green": 215, "Blue": 238},
    {"City":'海上haishang', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 47, "Green": 117, "Blue": 181},
    {"City":'海南hainan', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 142, "Green": 169, "Blue": 219},
    {"City":'成功ok', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 84, "Green": 130, "Blue": 53},
    {"City":'失败ng', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 255, "Green": 0, "Blue": 0},
    {"City":'部分成功part', "Tint": 0, "Vividness": 0, "Brightness": 0, "Red": 255, "Green": 153, "Blue": 0},
]

CityColors = [
    {"City":'酒泉Jiuquan', "Tint": 16, "Vivid": 201, "Bright": 177, "Red": 244, "Green": 176, "Blue": 132},
    {"City":'西昌Xichang', "Tint": 64, "Vivid": 99, "Bright": 165, "Red": 169, "Green": 208, "Blue": 142},
    {"City":'太原Taiyuan', "Tint": 30, "Vivid": 240, "Bright": 168, "Red": 255, "Green": 217, "Blue": 102},
    {"City":'文昌Wenchang', "Tint": 139, "Vivid": 142, "Bright": 201, "Red": 189, "Green": 215, "Blue": 238},
    {"City":'海上Haishang', "Tint": 139, "Vivid": 141, "Bright": 107, "Red": 47, "Green": 117, "Blue": 181},
    {"City":'海南Hainan', "Tint": 146, "Vivid": 124, "Bright": 170, "Red": 142, "Green": 169, "Blue": 219},
]

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
def getCityColorDict():
    colorDict = {}
    for color in CityColors:
        city = color['City']
        red = color['Red']
        green = color['Green']
        blue = color['Blue']
        # tint = color['Tint']
        # vivid = color['Vivid']
        # bright = color['Bright']
        colorDict[city] = (adjust_color(red, green, blue))
    return colorDict

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
                border: 1px solid black
                border-collapse: collapse;
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
                background-color: #F0F4F7; 
                border: 1px solid black
                border-collapse: collapse;
            }
            .border th, .border td {
                text-align: center;
                font-size: 16px;
                vertical-align: middle;
                border: 1px solid black;
                padding-left: 3px;
                padding-right: 3px;
            }
            .no-border {
                border: none;
            }
            .no-border th, .no-border td {
                border: none
                padding: 10px;
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
# textAligns = ['', 'left', 'right', 'center'] ''=center
# widths = ['', '300px', '', '']
# wraps = ['nowrap', 'nowrap', '', '']
def buildTableCell(columns, textAligns, widths, nowraps):
    html = '<TR>'
    for i, (column, textAlign, width, nowrap) in enumerate(zip(columns, textAligns, widths, nowraps)):
        textAlignStr = f'text-align: {textAlign}' if textAlign else ''
        widthStr = f'width: {width}' if width else ''
        styleStr = f'style="{textAlignStr}; {widthStr};"' if textAlign or width else ''
        if i == 7 or i == 8:
            classSrc = f'class="{CITY_MAPPING[column[:2] if column[1:2] == '海' else column]}"'
        else:
            classSrc = ''
        html += f'<TD {classSrc} {nowrap} {styleStr}>{column}</TD>'
    html += '</TR>\n'
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

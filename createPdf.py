import os
from glob import glob
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.platypus.flowables import Flowable

# 縦書きのフォントの処理をするためのクラス
class Tategaki(Flowable):
    def __init__(self,text):
        Flowable.__init__(self)
        self.text = text
    
    def draw(self):
        self.canv.rotate(-90)
        self.canv.drawString(0,0,self.text)
    
    def wrap(self,aW,aH):
        return self.canv._leading,-self.canv.stringWidth(self.text,self.canv._fontname,self.canv._fontsize)

df = pd.read_csv('unitafon.csv') # フォントのデータが書いてあるファイル
font_fd = 'fonta' # ファイルを保存する場所
save_folder = 'moji' # できたpdfファイルを保存するフォルダ

for i in range(len(df)):
    block = df['ブロック名'][i] # この文字のブロックの英語名
    font = df['フォント'][i] # この文字に使うフォントの名前
    h0 = int(df['範囲'][i],16) # ブロックのユニコードの開始（10進）
    h1 = h0+df['数'][i] # ブロックのユニコードの終わり（10進）
    pdf_file = os.path.join(save_folder,'%05d.pdf'%h0)
    # 0~Fの16進数を一番上に書く
    data = [['']+list(hex(i)[-1].upper() for i in range(16))]
    n = 0 # 何列目
    for x in range(h0,h1+1):
        if(n==0): #　一番左のコマにユニコードを書く（16進）
            da = [hex(x)[2:-1].upper()+'x']
        if(len(str(list[chr(x)]))==9):
            # モンゴル文字とパスパ文字だけは縦書きにする
            if(block in ['Mongolian','Phags-pa']):
                da.append(Tategaki(chr(x)))
            else:
                da.append(chr(x))
        else:
            da.append('')
        n += 1 # 次の列
        if(n==16): # すでに16列になったら次の行に移動する
            data.append(da)
            n = 0
    
    pagesize = [35*17+20,35*len(data)+15] # ページの広さ×高さ
    pcanvas = canvas.Canvas(pdf_file,pagesize=pagesize) # pdfページを作成する
    pdfmetrics.registerFont(TTFont(font,glob(os.path.join(font_fd,font,'*.ttf'))[0])) # フォント登録
    pcanvas.setFont('Helvetica',16) # ローマ字部分のフォント
    pcanvas.drawCentredString(pagesize[0]/2,pagesize[1]-15,block) # ヘッドにブロックの名前を書く
    # 表を作成する
    table = Table(data,colWidths=[45]+[35]*16,rowHeights=[25]+[35]*(len(data)-1))
    ts = [ # 表の中のフォントや色や線などのプロパティ
        ('TEXTCOLOR',(0,0),(-1,-1),colors.Color(1,1,1,1)), # 白い字
        ('BACKGROUND',(0,0),(-1,-1),colors.Color(0.3,0.1,0.3,1)), # 暗い紫色の背景
        ('FONT',(0,0),(-1,-1),'Helvetica',14), # ローマ字部分のフォント
        ('TEXTCOLOR',(1,1),(-1,-1),colors.Color(0.5,0,0,1)), # 茶色の字
        ('BACKGROUND',(1,1),(-1,-1),colors.Color(0.99,0.95,0.99,1)), # 薄桃色の背景
        ('FONT',(1,1),(-1,-1),font,16), # 文字表示のフォント
        ('GRID',(0,0),(-1,-1),1,colors.black), # 黒いグリッド
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('RIGHTPADDING',(0,0),(-1,-1),0),
    ]
    # 字がないコマは灰色にする
    for y in range(1,len(data)):
        for x in range(1,len(data[y])):
            if(data[y][x]==''):
                ts.append(('BACKGROUND',(x,y),(x,y),colors.Color(0.3,0.3,0.3,1)))
    # ある特定のブロックの配置の問題の対処
    if(block in ['Gunjala Gondi']):
        ts.append(('ALIGN',(1,1),(-1,-1),'LEFT'))
    if(block in ['Marchen','Khojki','Newa','Zanabazar Square','Chakma']):
        ts.append(('ALIGN',(1,1),(-1,-1),'RIGHT'))
    if(block in ['Balinese','Javanese']):
        ts.append(('VALIGN',(1,1),(-1,-1),'TOP'))
    table.setStyle(TableStyle(ts)) # 表のプロパティを設定する
    table.wrapOn(pcanvas,5,5)
    table.drawOn(pcanvas,5,5) # 表を描く
    pcanvas.save() # pdfファイルに保存する

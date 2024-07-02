from datetime import timedelta
from os import path
from sys import argv
from timeit import timeit

from myModules import myUtils

MUSIC_NAME_DICT = {
    'music/歌唱祖国音乐.mp3': 181.76,
    'music/momoe/001-としごろ.mp3': 159.268571,
    'music/momoe/002-叱らないでね.mp3': 162.168163,
    'music/momoe/003-ひとりぼっちのあなた.mp3': 184.894694,
    'music/momoe/004-青い果実.mp3': 150.151837,
    'music/momoe/005-おかしな恋人.mp3': 149.263673,
    'music/momoe/006-パパは恋人.mp3': 165.433469,
    'music/momoe/007-禁じられた遊び.mp3': 182.909388,
    'music/momoe/008-悩み多い14才.mp3': 145.789388,
    'music/momoe/009-春風のいたずら.mp3': 168.097959,
    'music/momoe/010-雨に濡れた少女.mp3': 190.92898,
    'music/momoe/011-15才の恋.mp3': 167.523265,
    'music/momoe/012-ひと夏の経験.mp3': 159.111837,
    'music/momoe/013-太陽の友達.mp3': 191.164082,
    'music/momoe/014-まばたきの夏.mp3': 147.043265,
    'music/momoe/015-教室を出たら大人.mp3': 172.094694,
    'music/momoe/016-ちっぽけな感傷.mp3': 184.058776,
    'music/momoe/017-清潔な恋.mp3': 196.91102,
    'music/momoe/018-冬の色.mp3': 181.890612,
    'music/momoe/019-伊豆の踊り子.mp3': 184.032653,
    'music/momoe/020-野菊の墓.mp3': 169.822041,
    'music/momoe/021-聖少女.mp3': 221.152653,
    'music/momoe/022-湖の決心.mp3': 197.250612,
    'music/momoe/023-春の奇蹟.mp3': 173.244082,
    'music/momoe/024-少年の海(出逢い).mp3': 216.137143,
    'music/momoe/025-美(み)え貝.mp3': 156.577959,
    'music/momoe/026-初恋時代.mp3': 169.560816,
    'music/momoe/027-夏ひらく青春.mp3': 188.577959,
    'music/momoe/028-ささやかな欲望.mp3': 199.88898,
    'music/momoe/029-ありがとうあなた.mp3': 216.346122,
    'music/momoe/030-白い約束.mp3': 224.470204,
    'music/momoe/031-山鳩.mp3': 185.70449,
    'music/momoe/032-空はこんなに青い.mp3': 202.527347,
    'music/momoe/033-愛に走って.mp3': 219.559184,
    'music/momoe/034-赤い運命.mp3': 192.078367,
    'music/momoe/035-木漏れ日.mp3': 225.201633,
    'music/momoe/036-碧色の瞳.mp3': 205.714286,
    'music/momoe/037-横須賀ストーリー.mp3': 232.306939,
    'music/momoe/038-GAME_IS_OVER.mp3': 211.983673,
    'music/momoe/039-陽炎(かげろう).mp3': 258.246531,
    'music/momoe/040-いま目覚めた子供のように.mp3': 234.945306,
    'music/momoe/041-パールカラーにゆれて.mp3': 188.003265,
    'music/momoe/042-赤い衝撃.mp3': 213.76,   
    'music/momoe/043-走れ風と共に.mp3': 194.821224,
    'music/momoe/044-オレンジ・ブロッサム・ブルース.mp3': 295.183673,
    'music/momoe/045-初恋草紙.mp3': 228.91102,
    'music/momoe/046-モノトーンの肖像画.mp3': 241.031837,
    'music/momoe/047-歌い継がれてゆく歌のように.mp3': 298.370612,
    'music/momoe/048-夢先案内人.mp3': 246.047347,
    'music/momoe/049-I_CAME_FROM_横須賀.mp3': 225.697959,
    'music/momoe/050-イミテイション・ゴールド.mp3': 203.180408,
    'music/momoe/051-鏡の中のある日.mp3': 269.714286,
    'music/momoe/052-愛のTWILIGHT_TIME.mp3': 188.238367,
    'music/momoe/053-秋桜(コスモス).mp3': 216.189388,
    'music/momoe/054-最後の頁.mp3': 256.444082,
    'music/momoe/055-寒椿.mp3': 266.161633,
    'music/momoe/056-青い羊歯(しだ)~アじアンタム.mp3': 267.232653,
    'music/momoe/057-赤い絆~レッド・センセーション.mp3': 251.794286,
    'music/momoe/058-口約束.mp3': 242.416327,
    'music/momoe/059-乙女座宮.mp3': 235.650612,
    'music/momoe/060-視線上のアリア.mp3': 218.174694,
    'music/momoe/061-プレイバックpart2.mp3': 202.187755,
    'music/momoe/062-ただよいの中で.mp3': 290.272653,
    'music/momoe/063-時の扉.mp3': 264.176327,
    'music/momoe/064-COSMOS(宇宙).mp3': 254.223673,
    'music/momoe/065-たそがれ祭り.mp3': 212.976327,
    'music/momoe/066-絶体絶命.mp3': 169.639184,
    'music/momoe/067-いい日旅立ち.mp3': 256.992653,
    'music/momoe/068-落葉の里.mp3': 218.462041,
    'music/momoe/069-スキャンダル~愛の日々.mp3': 245.942857,
    'music/momoe/070-霧雨楼.mp3': 241.580408,
    'music/momoe/071-ラスト・ソング.mp3': 379.742041,
    'music/momoe/072-曼珠沙華.mp3': 309.498776,
    'music/momoe/073-横須賀サンセット・サンライズ.mp3': 266.083265,
    'music/momoe/074-美・サイレント.mp3': 229.198367,
    'music/momoe/075-おだやかな構図.mp3': 245.942857,
    'music/momoe/076-想い出のミラージュ.mp3': 279.118367,
    'music/momoe/077-夜へ….mp3': 255.059592,
    'music/momoe/078-愛の嵐.mp3': 244.532245,
    'music/momoe/079-A_GOLD_NEEDLE_AND_SILVER_THREAD.mp3': 253.048163,
    'music/momoe/080-DANCIN’_IN_THE_RAIN.mp3': 340.114286,
    'music/momoe/081-CRY_FOR_ME.mp3': 273.188571,
    'music/momoe/082-しなやかに歌って.mp3': 290.507755,
    'music/momoe/083-娘たち.mp3': 296.254694,
    'music/momoe/084-愛染橋.mp3': 228.205714,
    'music/momoe/085-春爛漫.mp3': 220.630204,
    'music/momoe/086-あなたへの子守唄.mp3': 258.795102,
    'music/momoe/087-イントロダクション・春.mp3': 277.76,   
    'music/momoe/088-ロックンロール・ウィドウ.mp3': 241.240816,
    'music/momoe/089-アホカリプス・ラブ.mp3': 230.661224,
    'music/momoe/090-E=MC[↑]2.mp3': 275.983673,
    'music/momoe/091-さよならの向う側.mp3': 363.180408,
    'music/momoe/092-死と詩~death_and_poem.mp3': 203.937959,
    'music/momoe/093-不死鳥(フェニックス)伝説.mp3': 278.256327,
    'music/momoe/094-テレパシーナ.mp3': 318.432653,
    'music/momoe/095-This_is_my_trial~私の試練.mp3': 337.763265,
    'music/momoe/096-想い出のストロベリーフィールズ.mp3': 245.733878,
    'music/momoe/097-神様のおほし召し.mp3': 227.291429,
    'music/momoe/098-Crazy_Love.mp3': 289.802449,
    'music/momoe/099-一恵.mp3': 370.02449,
    'music/momoe/100-惜春(せきしゅん)通り.mp3': 193.227755,
}

MUSIC_NAME_LIST = [
    'music/momoe/001-としごろ.mp3',
    'music/momoe/002-叱らないでね.mp3',
    'music/momoe/003-ひとりぼっちのあなた.mp3',
    'music/momoe/004-青い果実.mp3',
    'music/momoe/005-おかしな恋人.mp3',
    'music/momoe/006-パパは恋人.mp3',
    'music/momoe/007-禁じられた遊び.mp3',
    'music/momoe/008-悩み多い14才.mp3',
    'music/momoe/009-春風のいたずら.mp3',
    'music/momoe/010-雨に濡れた少女.mp3',
    'music/momoe/011-15才の恋.mp3',
    'music/momoe/012-ひと夏の経験.mp3',
    'music/momoe/013-太陽の友達.mp3',
    'music/momoe/014-まばたきの夏.mp3',
    'music/momoe/015-教室を出たら大人.mp3',
    'music/momoe/016-ちっぽけな感傷.mp3',
    'music/momoe/017-清潔な恋.mp3',
    'music/momoe/018-冬の色.mp3',
    'music/momoe/019-伊豆の踊り子.mp3',
    'music/momoe/020-野菊の墓.mp3',
    'music/momoe/021-聖少女.mp3',
    'music/momoe/022-湖の決心.mp3',
    'music/momoe/023-春の奇蹟.mp3',
    'music/momoe/024-少年の海(出逢い).mp3',
    'music/momoe/025-美(み)え貝.mp3',
    'music/momoe/026-初恋時代.mp3',
    'music/momoe/027-夏ひらく青春.mp3',
    'music/momoe/028-ささやかな欲望.mp3',
    'music/momoe/029-ありがとうあなた.mp3',
    'music/momoe/030-白い約束.mp3',
    'music/momoe/031-山鳩.mp3',
    'music/momoe/032-空はこんなに青い.mp3',
    'music/momoe/033-愛に走って.mp3',
    'music/momoe/034-赤い運命.mp3',
    'music/momoe/035-木漏れ日.mp3',
    'music/momoe/036-碧色の瞳.mp3',
    'music/momoe/037-横須賀ストーリー.mp3',
    'music/momoe/038-GAME_IS_OVER.mp3',
    'music/momoe/039-陽炎(かげろう).mp3',
    'music/momoe/040-いま目覚めた子供のように.mp3',
    'music/momoe/041-パールカラーにゆれて.mp3',
    'music/momoe/042-赤い衝撃.mp3',
    'music/momoe/043-走れ風と共に.mp3',
    'music/momoe/044-オレンジ・ブロッサム・ブルース.mp3',
    'music/momoe/045-初恋草紙.mp3',
    'music/momoe/046-モノトーンの肖像画.mp3',
    'music/momoe/047-歌い継がれてゆく歌のように.mp3',
    'music/momoe/048-夢先案内人.mp3',
    'music/momoe/049-I_CAME_FROM_横須賀.mp3',
    'music/momoe/050-イミテイション・ゴールド.mp3',
    'music/momoe/051-鏡の中のある日.mp3',
    'music/momoe/052-愛のTWILIGHT_TIME.mp3',
    'music/momoe/053-秋桜(コスモス).mp3',
    'music/momoe/054-最後の頁.mp3',
    'music/momoe/055-寒椿.mp3',
    'music/momoe/056-青い羊歯(しだ)~アじアンタム.mp3',
    'music/momoe/057-赤い絆~レッド・センセーション.mp3',
    'music/momoe/058-口約束.mp3',
    'music/momoe/059-乙女座宮.mp3',
    'music/momoe/060-視線上のアリア.mp3',
    'music/momoe/061-プレイバックpart2.mp3',
    'music/momoe/062-ただよいの中で.mp3',
    'music/momoe/063-時の扉.mp3',
    'music/momoe/064-COSMOS(宇宙).mp3',
    'music/momoe/065-たそがれ祭り.mp3',
    'music/momoe/066-絶体絶命.mp3',
    'music/momoe/067-いい日旅立ち.mp3',
    'music/momoe/068-落葉の里.mp3',
    'music/momoe/069-スキャンダル~愛の日々.mp3',
    'music/momoe/070-霧雨楼.mp3',
    'music/momoe/071-ラスト・ソング.mp3',
    'music/momoe/072-曼珠沙華.mp3',
    'music/momoe/073-横須賀サンセット・サンライズ.mp3',
    'music/momoe/074-美・サイレント.mp3',
    'music/momoe/075-おだやかな構図.mp3',
    'music/momoe/076-想い出のミラージュ.mp3',
    'music/momoe/077-夜へ….mp3',
    'music/momoe/078-愛の嵐.mp3',
    'music/momoe/079-A_GOLD_NEEDLE_AND_SILVER_THREAD.mp3',
    'music/momoe/080-DANCIN’_IN_THE_RAIN.mp3',
    'music/momoe/081-CRY_FOR_ME.mp3',
    'music/momoe/082-しなやかに歌って.mp3',
    'music/momoe/083-娘たち.mp3',
    'music/momoe/084-愛染橋.mp3',
    'music/momoe/085-春爛漫.mp3',
    'music/momoe/086-あなたへの子守唄.mp3',
    'music/momoe/087-イントロダクション・春.mp3',
    'music/momoe/088-ロックンロール・ウィドウ.mp3',
    'music/momoe/089-アホカリプス・ラブ.mp3',
    'music/momoe/090-E=MC[↑]2.mp3',
    'music/momoe/091-さよならの向う側.mp3',
    'music/momoe/092-死と詩~death_and_poem.mp3',
    'music/momoe/093-不死鳥(フェニックス)伝説.mp3',
    'music/momoe/094-テレパシーナ.mp3',
    'music/momoe/095-This_is_my_trial~私の試練.mp3',
    'music/momoe/096-想い出のストロベリーフィールズ.mp3',
    'music/momoe/097-神様のおほし召し.mp3',
    'music/momoe/098-Crazy_Love.mp3',
    'music/momoe/099-一恵.mp3',
    'music/momoe/100-惜春(せきしゅん)通り.mp3',
    'music/momoe/101-輪廻.mp3',
    'music/momoe/102-あやつり人形館.mp3',
    'music/momoe/103-琥珀の季節.mp3',
    'music/momoe/104-闇の薫り.mp3',
    'music/momoe/105-Jigsaw_Puzzle.mp3',
    'music/momoe/106-幕間の風景.mp3',
    'music/momoe/107-恋は千里眼.mp3',
    'music/momoe/108-昨日までの顔.mp3',
    'music/momoe/109-野薔薇.mp3',
    'music/momoe/110-愛がひとつあれば.mp3',
    'music/momoe/111-感傷旅行.mp3',
    'music/momoe/112-感じる季節.mp3',
    'music/momoe/113-燃える海.mp3',
    'music/momoe/114-少女の誇り.mp3',
    'music/momoe/115-あなたが死んだら.mp3',
    'music/momoe/116-哀愁のコニーアイランド.mp3',
    'music/momoe/117-BLACK_CAB(ロンドン・タクシー).mp3',
    'music/momoe/118-序曲.mp3',
    'music/momoe/119-海から零へ.mp3',
    'music/momoe/120-MissBoy.mp3',
    'music/momoe/121-ブラックボール.mp3',
    'music/momoe/122-WHO.mp3',
    'music/momoe/123-スペース・トラブル危機一髪.mp3',
    'music/momoe/124-ダンシング・スターシャイン.mp3',
    'music/momoe/125-空から無限大.mp3',
    'music/momoe/126-謝肉祭.mp3',
]

MUSIC_TIME_LIST = [
    159.268571,#'001-としごろ.mp3',
    162.168163,#'002-叱らないでね.mp3',
    184.894694,#'003-ひとりぼっちのあなた.mp3',
    150.151837,#'004-青い果実.mp3',
    149.263673,#'005-おかしな恋人.mp3',
    165.433469,#'006-パパは恋人.mp3',
    182.909388,#'007-禁じられた遊び.mp3',
    145.789388,#'008-悩み多い14才.mp3',
    168.097959,#'009-春風のいたずら.mp3',
    190.92898, #'010-雨に濡れた少女.mp3',
    167.523265,#'011-15才の恋.mp3',
    159.111837,#'012-ひと夏の経験.mp3',
    191.164082,#'013-太陽の友達.mp3',
    147.043265,#'014-まばたきの夏.mp3',
    172.094694,#'015-教室を出たら大人.mp3',
    184.058776,#'016-ちっぽけな感傷.mp3',
    196.91102, #'017-清潔な恋.mp3',
    181.890612,#'018-冬の色.mp3',
    184.032653,#'019-伊豆の踊り子.mp3',
    169.822041,#'020-野菊の墓.mp3',
    221.152653,#'021-聖少女.mp3',
    197.250612,#'022-湖の決心.mp3',
    173.244082,#'023-春の奇蹟.mp3',
    216.137143,#'024-少年の海(出逢い).mp3',
    156.577959,#'025-美(み)え貝.mp3',
    169.560816,#'026-初恋時代.mp3',
    188.577959,#'027-夏ひらく青春.mp3',
    199.88898, #'028-ささやかな欲望.mp3',
    216.346122,#'029-ありがとうあなた.mp3',
    224.470204,#'030-白い約束.mp3',
    185.70449, #'031-山鳩.mp3',
    202.527347,#'032-空はこんなに青い.mp3',
    219.559184,#'033-愛に走って.mp3',
    192.078367,#'034-赤い運命.mp3',
    225.201633,#'035-木漏れ日.mp3',
    205.714286,#'036-碧色の瞳.mp3',
    232.306939,#'037-横須賀ストーリー.mp3',
    211.983673,#'038-GAME_IS_OVER.mp3',
    258.246531,#'039-陽炎(かげろう).mp3',
    234.945306,#'040-いま目覚めた子供のように.mp3',
    188.003265,#'041-パールカラーにゆれて.mp3',
    213.76,    #'042-赤い衝撃.mp3',
    194.821224,#'043-走れ風と共に.mp3',
    295.183673,#'044-オレンジ・ブロッサム・ブルース.mp3',
    228.91102, #'045-初恋草紙.mp3',
    241.031837,#'046-モノトーンの肖像画.mp3',
    298.370612,#'047-歌い継がれてゆく歌のように.mp3',
    246.047347,#'048-夢先案内人.mp3',
    225.697959,#'049-I_CAME_FROM_横須賀.mp3',
    203.180408,#'050-イミテイション・ゴールド.mp3',
    269.714286,#'051-鏡の中のある日.mp3',
    188.238367,#'052-愛のTWILIGHT_TIME.mp3',
    216.189388,#'053-秋桜(コスモス).mp3',
    256.444082,#'054-最後の頁.mp3',
    266.161633,#'055-寒椿.mp3',
    267.232653,#'056-青い羊歯(しだ)~アじアンタム.mp3',
    251.794286,#'057-赤い絆~レッド・センセーション.mp3',
    242.416327,#'058-口約束.mp3',
    235.650612,#'059-乙女座宮.mp3',
    218.174694,#'060-視線上のアリア.mp3',
    202.187755,#'061-プレイバックpart2.mp3',
    290.272653,#'062-ただよいの中で.mp3',
    264.176327,#'063-時の扉.mp3',
    254.223673,#'064-COSMOS(宇宙).mp3',
    212.976327,#'065-たそがれ祭り.mp3',
    169.639184,#'066-絶体絶命.mp3',
    256.992653,#'067-いい日旅立ち.mp3',
    218.462041,#'068-落葉の里.mp3',
    245.942857,#'069-スキャンダル~愛の日々.mp3',
    241.580408,#'070-霧雨楼.mp3',
    379.742041,#'071-ラスト・ソング.mp3',
    309.498776,#'072-曼珠沙華.mp3',
    266.083265,#'073-横須賀サンセット・サンライズ.mp3',
    229.198367,#'074-美・サイレント.mp3',
    245.942857,#'075-おだやかな構図.mp3',
    279.118367,#'076-想い出のミラージュ.mp3',
    255.059592,#'077-夜へ….mp3',
    244.532245,#'078-愛の嵐.mp3',
    253.048163,#'079-A_GOLD_NEEDLE_AND_SILVER_THREAD.mp3',
    340.114286,#'080-DANCIN’_IN_THE_RAIN.mp3',
    273.188571,#'081-CRY_FOR_ME.mp3',
    290.507755,#'082-しなやかに歌って.mp3',
    296.254694,#'083-娘たち.mp3',
    228.205714,#'084-愛染橋.mp3',
    220.630204,#'085-春爛漫.mp3',
    258.795102,#'086-あなたへの子守唄.mp3',
    277.76,    #'087-イントロダクション・春.mp3',
    241.240816,#'088-ロックンロール・ウィドウ.mp3',
    230.661224,#'089-アホカリプス・ラブ.mp3',
    275.983673,#'090-E=MC[↑]2.mp3',
    363.180408,#'091-さよならの向う側.mp3',
    203.937959,#'092-死と詩~death_and_poem.mp3',
    278.256327,#'093-不死鳥(フェニックス)伝説.mp3',
    318.432653,#'094-テレパシーナ.mp3',
    337.763265,#'095-This_is_my_trial~私の試練.mp3',
    245.733878,#'096-想い出のストロベリーフィールズ.mp3',
    227.291429,#'097-神様のおほし召し.mp3',
    289.802449,#'098-Crazy_Love.mp3',
    370.02449, #'099-一恵.mp3',
    193.227755,#'100-惜春(せきしゅん)通り.mp3',
    305.084082,#"101-輪廻.mp3"
    252.447347,#"102-あやつり人形館.mp3"
    277.368163,#"103-琥珀の季節.mp3"
    268.956735,#"104-闇の薫り.mp3"
    275.879184,#"105-Jigsaw_Puzzle.mp3"
    229.198367,#"106-幕間の風景.mp3"
    319.921633,#"107-恋は千里眼.mp3"
    186.313256,#"108-昨日までの顔.mp3"
    219.227567,#"109-野薔薇.mp3"
    192.034067,#"110-愛がひとつあれば.mp3"
    194.019378,#"111-感傷旅行.mp3"
    218.234938,#"112-感じる季節.mp3"
    197.441438,#"113-燃える海.mp3"
    183.074067,#"114-少女の誇り.mp3"
    190.257756,#"115-あなたが死んだら.mp3"
    261.172245,#"116-哀愁のコニーアイランド.mp3"
    266.370612,#"117-BLACK_CAB(ロンドン・タクシー)
    168.489796,#"118-序曲.mp3"
    328.960000,#"119-海から零へ.mp3"
    242.390204,#"120-Miss_Boy.mp3"
    280.711837,#"121-ブラックボール.mp3"
    336.274286,#"122-WHO.mp3"
    308.793469,#"123-スペース・トラブル危機一髪.mp
    241.057959,#"124-ダンシング・スターシャイン.mp
    147.017143,#"125-空から無限大.mp3"
    237.714286,#"126-謝肉祭.mp3"
]

################################################################################################
# TODO: how to use dict for music name and duration
def findCombinationsNew(musicList, musicDict, index, current_tracks, current_duration, video_duration, results, count, threshold):
    if len(results) == count:
        return
    
    if abs(current_duration - video_duration) <= threshold:  # Adjust this threshold as necessary
        results.append((f'{current_duration:.6f}', current_tracks.copy()))

    # for i in range(index, len(musicList)):
    for i, music in enumerate(musicList[index:], index):
        if current_duration + musicDict[music] <= video_duration:  # Prune the search space
            current_tracks.append(musicDict[music])
            findCombinations(musicList, musicDict, i + 1, current_tracks, current_duration + musicDict[music], video_duration, results, count, threshold)
            current_tracks.pop()  # Backtrack after exploring this path

################################################################################################
def findCombinations(musicList, timeList, index, current_tracks, current_duration, video_duration, results, count, threshold):
    if len(results) == count:
        return
    
    if abs(current_duration - video_duration) <= threshold:  # Adjust this threshold as necessary
        # makeMusicItem(f'{current_duration:.6f}', current_tracks.copy())
        results.append((f'{current_duration:.6f}', current_tracks.copy()))

    for i in range(index, len(musicList)):
        if current_duration + timeList[i] <= video_duration:  # Prune the search space
            current_tracks.append(musicList[i])
            findCombinations(musicList, timeList, i + 1, current_tracks, current_duration + timeList[i], video_duration, results, count, threshold)
            current_tracks.pop()  # Backtrack after exploring this path

################################################################################################
def makeMusicItem(duration, tracks):
    return (duration, tracks)

################################################################################################
def matchMusics2Video(videoName, musicList=MUSIC_NAME_LIST, favorites=[], threshold=1, index=0, count=100):
    videoTime = myUtils.getFileDuration(videoName)

    if len(musicList) == 1:
        n = int(videoTime) // int(MUSIC_NAME_DICT[musicList[0]])
        duration = f'{MUSIC_NAME_DICT[musicList[0]] * n:.6f}'
        tracks = (f'{musicList[0]},' * n)[:-1].split(',')
        results = [(f'{duration}', tracks)]
    else:
        musicList = [path.abspath(music) for music in musicList]
        timeList = MUSIC_TIME_LIST
        favoritesTime = 0
        results = []

        if favorites:
            musicList, timeList, favoritesTime = myUtils.removeItemsFromTwoLists(musicList, timeList, favorites)
        else:
            favorites = []

        findCombinations(musicList, timeList, index, favorites, favoritesTime, videoTime, results, count, threshold)

    if results:
        sortedResults = sorted(results, key=lambda x: x[0], reverse=False)
        lines = ''

        for i, result in enumerate(sortedResults, 1):
            print(f'{i:03}: {result[0]} {[path.basename(r) for r in result[1]]}')
            lines += f'{','.join(result[1])}\n'

        print(f'\n{videoName=}, {videoTime=}, {index=}, {count=}, {threshold=}\n')
        listFilename = f'mergelist/{path.basename(videoName).replace(".mp4", ".txt")}'
        myUtils.saveTextFile(listFilename, lines, openFile=False)
 
        for i, favorite in enumerate(favorites, 1):
            print(f'favorite{i:02}: {favorite.split('\\')[-1]}')
    else:
        print(f'No match musics for threshold={threshold}')
        print(f'\n{videoName=}, {videoTime=}, {index=}, {count=}, {threshold=}')

################################################################################################
def showUsage():
    print('Match Msuic to Video durartion.')
    print(f'python {argv[0]} videoName musicList favorites threshold index count')
    print('Usage:')
    print('  videoName: Video filename')
    print('  musicList: music filename list to be matched')
    print('  favorites: Favorite music filename list')
    print('  threshold: The threshold in seconds between video and music sum durations')
    print('  index: start index of music files list')
    print('  count: The amount of ouput')

################################################################################################
def parseArgv():
    if len(argv) > 6:
        videoName = argv[1]
        musicList = argv[2]
        favorites = argv[3]
        threshold = float(argv[4])
        index = int(argv[5])
        count = int(argv[6])
    elif len(argv) > 5:
        videoName = argv[1]
        musicList = argv[2]
        favorites = argv[3]
        threshold = float(argv[4])
        index = int(argv[5])
        count = 100
    elif len(argv) > 4:
        videoName = argv[1]
        musicList = argv[2]
        favorites = argv[3]
        threshold = float(argv[4])
        index = 0
        count = 100
    elif len(argv) > 3:
        videoName = argv[1]
        musicList = argv[2]
        favorites = argv[3]
        threshold = 1
        index = 0
        count = 100
    elif len(argv) > 2:
        videoName = argv[1]
        musicList = argv[2]
        favorites = []
        threshold = 1
        index = 0
        count = 100
    elif len(argv) > 1:
        videoName = argv[1]
        musicList = []
        favorites = []
        threshold = 1
        index = 0
        count = 100

    if musicList and myUtils.isTextFile(musicList):
        musicList = myUtils.readTextFile(musicList, True)
    else:
        musicList = MUSIC_NAME_LIST if not musicList else musicList.split(',')

    if favorites:
        if myUtils.isTextFile(favorites):
            favorites = myUtils.readTextFile(favorites, True)
            favorites = [path.abspath(item) for item in favorites]
        else:
            favorites = [path.abspath(item) for item in favorites.split(',')]

    return videoName, musicList, favorites, threshold, index, count

################################################################################################
def main():
    myUtils.setStartTime()
    if len(argv) == 1:
        showUsage()
        return
    
    videoName, musicList, favorites, threshold, index, count = parseArgv()
    if not myUtils.isVideoFile(videoName):
        showUsage()
        return

    matchMusics2Video(videoName, musicList, favorites, threshold, index, count)
    myUtils.showRunTime()

################################################################################################
def findMomoeSongs():
    momoeAllList = [m.split(':')[-1] for m in myUtils.readTextFile('music/momoe/momoeAll.txt', True)]
    resultList = sorted(momoeAllList)
    myUtils.saveListToTextFile('music/momoe/momoeLast.txt', resultList)
    return

    momoe100List = myUtils.readTextFile('music/momoe/momoe100.txt', True)
    momoeList = myUtils.readTextFile('music/momoe/momoe.txt', True)
    momoe100Dict = {m.split('-')[-1]: m for m in momoe100List}
    momoeDict = {m.split('-')[-1]: m for m in momoeList}

    for k, v in momoeDict.items():
        if k not in momoe100Dict:
            momoe100Dict[k] = v

    resultDict = myUtils.sortDictByKey(momoe100Dict)
    myUtils.saveDictToTextFile('music/momoe/momoeAll.txt', resultDict)


################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}')
    
if __name__ == "__main__":
    # showRunTime("findMomoeSongs()")
    showRunTime("main()")

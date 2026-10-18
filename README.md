This repository includes all Python scripts and windows batches to parse and predict China Launch Vehicles from NOTAM and MSA notices.

The historical launch data is saved in [./data/ChinaRocketLaunch.xlsx](./data/ChinaRocketLaunch.xlsx), it has to be updated when new launch issued!

# 1. NOTAM

 Parse NOTAM for China Launch Vehicles and create KML and text files in folder [./temp](./temp)

```
2026/10/16  17:52             4,954 2026年10月21日11时36分黄海日照+近地轨道.kml
2026/10/16  17:52               228 2026年10月21日11时36分黄海日照+近地轨道.txt
2026/10/16  18:15             3,927 2026年10月22日10时58分文昌_海南_西昌+近地轨道.kml
2026/10/16  18:15               228 2026年10月22日10时58分文昌_海南_西昌+近地轨道.txt
2026/10/16  17:52             4,442 2026年10月22日11时00分文昌_海南_西昌_酒泉+近地轨道.kml
2026/10/16  17:52               228 2026年10月22日11时00分文昌_海南_西昌_酒泉+近地轨道.txt
2026/10/16  18:15             2,724 2026年10月24日03时00分东海上海_酒泉_黄海日照+近地轨道.kml
2026/10/16  18:15               228 2026年10月24日03时00分东海上海_酒泉_黄海日照+近地轨道.txt
2026/10/17  10:47               692 notam20261017-104734.txt
```

The notam20261017-104734.txt file looks like:

```
NOTAM发射预测
================================
01A: ZSHA,A5222/26,2026/10/21 03:29,2026/10/21 03:50;N35°23',E119°35'+20000
01B: ZSHA,A5223/26,2026/10/21 03:30,2026/10/21 03:54;N35°17',E120°11'|N35°00',E120°46'|N34°46',E120°36'|N35°05',E120°01'

02A: RPHI,B5549/26,2026/10/22 02:50,2026/10/22 03:15;N13°17',E115°55'|N13°38',E116°22'|N12°46',E117°03'|N12°26',E116°37'
02B: RPHI,B5550/26,2026/10/22 02:51,2026/10/22 03:26;N08°00',E119°57'|N08°26',E120°32'|N07°35',E121°13'|N07°28',E121°10'|N07°08',E120°44'|N07°08',E120°37'

03A: RJJJ,P5065/26,2026/10/23 18:00,2026/10/28 21:00;N30°43',E125°49'|N30°15',E126°36'|N29°48',E126°15'|N30°14',E125°33'
```

- Prase from [notams.aim.faa.gov/notamSearch](https://notams.aim.faa.gov/notamSearch/)
  `python notam.py`
- Parse NOTAM from local file [./data/notam.txt](./data/notam.txt)
  `python notam.py local`
- Parse MSA from local file [./data/msa.txt](./data/msa.txt)
  `python notam.py local`

# 2. KML file

- Compare KML file with historical files
  `python compare.py new_kml_filename`

```
Comapre to history KML files...
2026年10月21日??时??分黄海日照东方航天港号谷神星一号海.kml IoU 2024年05月29日16时12分黄海日照东方航天港号谷神星一号海.kml
         2 = Max DZ Count
    36.58% = Overall IoU
    73.15% = ZSHA/A5223/26 IoU ZSHA/A1309/24

2026年10月21日??时??分黄海日照东方航天港号谷神星一号海.kml IoU 2025年08月09日00时31分黄海日照东方航天港号捷龙三号.kml
         2 = Max DZ Count
    23.28% = Overall IoU
    46.56% = ZSHA/A5223/26 IoU ZSHA/A2555/25

2026年10月21日??时??分黄海日照东方航天港号谷神星一号海.kml IoU 2024年12月19日18时18分黄海日照东方航天港号谷神星一号海.kml
         2 = Max DZ Count
    36.58% = Overall IoU
    73.15% = ZSHA/A5223/26 IoU ZSHA/A4260/24

2026年10月21日??时??分黄海日照东方航天港号谷神星一号海.kml IoU 2025年09月09日03时48分黄海日照东方航天港号捷龙三号.kml
         2 = Max DZ Count
    25.37% = Overall IoU
    50.74% = ZSHA/A5223/26 IoU ZSHA/A2928/25

2026年10月21日??时??分黄海日照东方航天港号谷神星一号海.kml IoU 2025年05月19日15时38分黄海日照东方航天港号谷神星一号海.kml
         2 = Max DZ Count
    36.58% = Overall IoU
    73.15% = ZSHA/A5223/26 IoU ZSHA/A1274/25

2026年10月21日??时??分黄海日照东方航天港号谷神星一号海.kml IoU 2026年01月16日04时10分黄海日照德浮15001号谷神星一号海.kml
         2 = Max DZ Count
    36.58% = Overall IoU
    73.15% = ZSHA/A5223/26 IoU ZSHA/A0116/26

2026年10月21日??时??分黄海日照东方航天港号谷神星一号海.kml IoU 2025年09月24日15时56分黄海日照东方航天港号捷龙三号.kml
         2 = Max DZ Count
    26.66% = Overall IoU
    53.31% = ZSHA/A5223/26 IoU ZSHA/A3354/25
```
The matched files saved to [./temp/match](./temp/match)
![](./images/2026年10月21日黄海日照东方航天港号谷神星一号海重叠轨道落区发射历史（截止2026年10月18日）.png)

Other files saved to [./temp/unmatch](./temp/unmatch)
![](./images/2026年10月21日黄海日照东方航天港号谷神星一号海同发射地相同轨道落区发射历史（截止2026年10月18日）.png)
![](./images/2026年10月21日黄海日照东方航天港号谷神星一号海同发射地不同轨道落区发射历史（截止2026年10月18日）.png)

- Show KML files on map
  `python showkml.py`
  ![](./images/showkmlScreen.png)
- Create Luanch Calendar
  The 202610.png will be saved to [./calendar](./calendar)
  `python cal.py 202610`
  ![](./calendar/202610.png)

# 3. Machine Learning

 There are 4 models of RF(RandomForest), ET(ExtraTrees), GB(GradientBossting) and HGB(HistGradientBossting) in folder [./historical](./historical).

```
2026/10/16  17:48         4,419,563 feature-GEO_database.csv
2026/10/16  17:48        64,644,086 feature-GEO_target-BINARY_model-ET.pkl
2026/10/16  17:48         2,284,854 feature-GEO_target-BINARY_model-GB.pkl
2026/10/16  17:48         2,440,070 feature-GEO_target-BINARY_model-HGB.pkl
2026/10/16  17:48        22,319,782 feature-GEO_target-BINARY_model-RF.pkl
2026/10/16  17:48       192,818,489 feature-GEO_target-CLASSES_model-ET.pkl
2026/10/16  17:48        13,454,969 feature-GEO_target-CLASSES_model-GB.pkl
2026/10/16  17:48         9,180,393 feature-GEO_target-CLASSES_model-HGB.pkl
2026/10/16  17:48        96,109,241 feature-GEO_target-CLASSES_model-RF.pkl
2026/10/16  17:48         1,686,419 feature-IoU_database.csv
2026/10/16  17:48        16,970,507 feature-IoU_target-BINARY_model-ET.pkl
2026/10/16  17:48           896,923 feature-IoU_target-BINARY_model-GB.pkl
2026/10/16  17:48         1,049,195 feature-IoU_target-BINARY_model-HGB.pkl
2026/10/16  17:48        14,427,323 feature-IoU_target-BINARY_model-RF.pkl
2026/10/16  17:48            50,816 kml_names-GEO.csv
2026/10/16  17:48            50,816 kml_names-IoU.csv
```

- Create Models
  `python ml.py build`
- Predict new launch kml file
  `python ml.py predict new_kml_filename`

# 4 Others
- Create varivarious kinds of picture and video
```
Usage:
  plot                       :显示画面
  plot yao                   :显示现役火箭未使用遥号
  plot 年                    :生成年全部发射
  plot 年月                  :生成年月全部发射
  plot 年/年月 下记其他选项  :生成年其他选项发射
  plot 火箭名                :生成火箭发射
  plot 载荷名                :生成包含载荷名发射
  plot 发射地                :生成发射地发射
  plot regexp                :生成符合正则表达式发射
  plot 遥?                   :生成火箭发射遥?
  plot "^载荷名"             :生成载荷名开始的发射
  plot "?月"                 :生成?月发射
  plot 春节                  :生成春节前后发射
  plot 年初年末              :生成年初年末发射
  plot 首飞                  :生成首飞发射
  plot 空间站                :生成空间站相关发射
  plot 上面级                :生成上面级发射
```
![](./images/plotScreen.png)


- Parse Chtml files from hinese Launchers of [https://forum.nasaspaceflight.com/index.php?board=40.0](https://forum.nasaspaceflight.com/index.php?board=40.0)
`python nsf.py`
The [nsfLinkList.html](./temp/nsfLinkList.html) file created in folder [./temp/](./temp)
![](./images/nsfLinkList.png)

The html files saved in folder [./temp/nsf](./temp/nsf])
```
2026/10/16  20:53            82,161 https___forum.nasaspaceflight.com_index.php_board=40.0.html
2026/10/16  20:53            84,954 https___forum.nasaspaceflight.com_index.php_board=40.50.html
2026/10/16  20:53            76,835 https___forum.nasaspaceflight.com_index.php_board=40.100.html
2026/10/16  20:53            81,519 https___forum.nasaspaceflight.com_index.php_board=40.150.html
2026/10/16  20:53            78,101 https___forum.nasaspaceflight.com_index.php_board=40.200.html
2026/10/16  20:55            81,249 https___forum.nasaspaceflight.com_index.php_board=40.250.html
2026/10/16  20:55            79,625 https___forum.nasaspaceflight.com_index.php_board=40.300.html
2026/10/16  20:55            84,082 https___forum.nasaspaceflight.com_index.php_board=40.350.html
2026/10/16  20:55            84,871 https___forum.nasaspaceflight.com_index.php_board=40.400.html
2026/10/16  20:55            85,236 https___forum.nasaspaceflight.com_index.php_board=40.450.html
2026/09/04  10:13            86,732 https___forum.nasaspaceflight.com_index.php_board=40.500.html
2026/09/04  10:13            88,949 https___forum.nasaspaceflight.com_index.php_board=40.550.html
2026/09/04  10:13            85,952 https___forum.nasaspaceflight.com_index.php_board=40.600.html
2026/09/04  10:13            84,953 https___forum.nasaspaceflight.com_index.php_board=40.650.html
2026/09/04  10:13            93,219 https___forum.nasaspaceflight.com_index.php_board=40.700.html
2026/09/04  10:13            89,908 https___forum.nasaspaceflight.com_index.php_board=40.750.html
2026/09/04  10:13            88,562 https___forum.nasaspaceflight.com_index.php_board=40.800.html
2026/09/04  10:13            85,788 https___forum.nasaspaceflight.com_index.php_board=40.850.html
2026/09/04  10:13            89,522 https___forum.nasaspaceflight.com_index.php_board=40.900.html
2026/09/04  10:13            87,856 https___forum.nasaspaceflight.com_index.php_board=40.950.html
2026/09/04  10:13            83,774 https___forum.nasaspaceflight.com_index.php_board=40.1000.html
2026/09/04  10:13            81,671 https___forum.nasaspaceflight.com_index.php_board=40.1050.html
2026/09/04  10:13            73,077 https___forum.nasaspaceflight.com_index.php_board=40.1100.html
2026/09/04  10:13            64,273 https___forum.nasaspaceflight.com_index.php_board=40.1150.html
```


- Show Launch candidate Date and time of Shenzhou and Tianzhou spaceship.
  `python css.py "酒泉:20261117,20261125"`
  ![](./images/酒泉.png)


- Create Statistics on Chinese Carrier Rocket Launches Video with music
`mergenew.bat`
```
====================================================================
Run plot.py to Create All Chart Bar Race Videos in other command window
Check merge list for new page
Keep file ./mergeList/ListImageThisYear.txt!
Keep file ./mergeList/ListImageMonth.txt!
Keep file ./mergeList/ListImageLocation.txt!
Keep file ./mergeList/ListImageRocket.txt!
Keep file ./mergeList/ListImageAll.txt!
Keep file ./mergeList/ListVideoBarChartRace.txt!
Keep file ./mergeList/ListVideoAll.txt!
Finished in 0:00:00.031338

0  - Create cover.mp4
1  - Create 中国运载火箭发射统计（今年）.mp4 by mergelist\ListImageThisYear.txt
2  - Create 中国运载火箭发射统计（月别）.mp4 by mergelist\ListImageMonth.txt
3  - Create 中国运载火箭发射统计（地别）.mp4 by mergelist\ListImageLocation.txt
4  - Create 中国运载火箭发射统计（箭别）.mp4 by mergelist\ListImageRocket.txt
5  - Create 中国运载火箭发射统计（全部）.mp4 by mergelist\ListImageAll.txt
6  - Create 中国运载火箭发射动态图.mp4 by mergelist\ListVideoBarChartRace.txt
7  - Create 中国运载火箭发射统计.mp4 by mergelist\ListVideoAll.txt
81 - Create 中国运载火箭发射统计-祝福祖国.mp4 with 祝福祖国.mp3
82 - Create 中国运载火箭发射统计-歌唱祖国音乐.mp4 with 歌唱祖国音乐.mp3
83 - Create 中国运载火箭发射统计-山口百惠.mp4 with 山口百惠歌曲
91 - Create 中国航天员在轨历史动态条形图-歌唱祖国音乐.mp4 with 歌唱祖国音乐.mp3
92 - Create 中国航天员在轨历史动态条形图-山口百惠.mp4 with 山口百惠歌曲
A0 - Create calendar Videos by mergelist\ListImageCalendar.txt
A1 - Create calendarLastMonth Videos by mergelist\ListImageCalendarLastMonth.txt
A2 - Create calendar.mp4 by mergelist\ListVideoCalendar.txt
A3 - Create calendar-歌唱祖国音乐.mp4 with 歌唱祖国音乐.mp3
A4 - Create calendar-山口百惠.mp4 with 山口百惠歌曲
X  - Exit
Select :
```

- Parse [m.ctrip.com/webapp/vacations/tour](http:s//m.ctrip.com/webapp/vacations/tour)
`python trip.py`
```
Searching 捷程旅行...

Saved to ./temp/捷程旅行.html!

Title01: 科学探索·海南文昌半日火箭发射观礼亲子营丨【未来之旅】文昌发射观礼亲子团
 Link01: https://m.ctrip.com/webapp/vacations/tour/detail?productid=33466809

Title02: 科学探索·海南4天3晚文昌火箭观礼亲子游丨【未来之旅】航天科普+日月湾冲浪+浆板体验半自助游
 Link02: https://m.ctrip.com/webapp/vacations/tour/detail?productid=34152808

Title03: 科学探索·海南4天3晚文昌火箭发射观礼亲子游丨【未来之旅】航天科普+帆船营体验+海龟保育
 Link03: https://m.ctrip.com/webapp/vacations/tour/detail?productid=34905924

Title04: 科学探索·文昌3天2晚航天亲子夏令营丨【未来之旅】海南文昌火箭发射观礼+卫星基地参观+航天超算中心+陨石馆+科普馆+航天育种基地+航天讲座+手工活动亲子夏令营
 Link04: https://m.ctrip.com/webapp/vacations/tour/detail?productid=62577387


各旅行社发射预测2026/10/18 16:38:44
===================================
01 2026/10/22: 文昌(捷程)
02 2026/10/27: 文昌(捷程)
03 2026/11/03: 文昌(捷程)
```
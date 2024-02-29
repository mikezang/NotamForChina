#!/bin/bash 
    #Description: Images downloader
    #Filename: img_downloader.sh
   
    if [ $# -ne 1 ]; then
        echo "Usage: $0 URL"
        exit -1 
    fi
   
    for i in {1..2}
    do
        case $1 in
            -d) shift; directory=$1; shift ;;
             *) url=${url:-$1}; shift;;
        esac
    done
   
    baseurl=$(echo $url | egrep -o "https?://[a-z.]+")
    echo "baseurl: $baseurl"

#    curl --silent $url | egrep -o "(<td>.*</td><td|class=\"/[^>]*(\.jpg|\.gif|\.png))" | sed "s|^class=\"/|$baseurl/|" | sed "s|<td>产品编号：\(.*\)</td><td|\1|g" | sed "s|<td>产品名称：\(.*\)</td><td|\1|g" | sed "s|<td>数 量：\(.*\)PCS</td><td|\1|g" | sed "s|<td>彩盒规格：*.*.||g" | awk '{printf "%s" (NR%5==0?RS:FS),$1}'

    curl --silent $url | egrep -o "(<td>.*</td><td|class=\"/[^>]*(\.jpg|\.JPG|\.gif|\.GIF|\.png|\.PNG))" | 
        sed "s|^class=\"/||;
             s|<td>产品编号：\(.*\)</td><td|\1|g;
             s|<td>产品名称：\(.*\)</td><td|\1|g;
             s|<td>数 量：\(.*\)PCS</td><td|\1|g;
             s|<td>彩盒规格：*.*.||g" | 
        awk '{ if($1) printf $1 ","; else print RS; }' | 
        awk '!/^$/' | 
        awk '!/^upload/' |
        awk -F $',' '{print "brand, theme, "$1","$3","$4, $2, $5}'


exit

#    sed -i "s|^/|$baseurl/|" /tmp/$$.list
#
    while read filename;
    do
        curl -s -O "$baseurl/$filename" 
        echo "$baseurl/$filename" 
    done < /tmp/$$.list


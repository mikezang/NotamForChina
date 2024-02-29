#!/bin/bash 
    #Description: Images downloader
    #Filename: img_downloader.sh
   
    if [ $# -ne 3 ]; then
        echo "Usage: $0 URL -d DIRECTORY"
        exit -1 
    fi
   
    for i in {1..4}
    do
        case $1 in
            -d) shift; directory=$1; shift ;;
             *) url=${url:-$1}; shift;;
        esac
    done
   
    mkdir -p $directory;
    baseurl=$(echo $url | egrep -o "https?://[a-z.]+")
    echo "baseurl: $baseurl"

#    curl --silent $url | egrep -o "<img .* src=[^>]*>"
#    sed 's/<img .* src=\"\([^"]*\).*/\1/g' > /tmp/$$.list
#    curl --silent $url | egrep -o "src=[^>]*(\.jpg|\.gif|\.png)" | sed 's/src=\"\(.*\)/\1/g' > /tmp/$$.list 
    curl --silent $url | egrep -o "class=[^>]*(\.jpg|\.gif|\.png)" | sed 's/class=\"\(.*\)/\1/g' > /tmp/$$.list 
    sed -i "s|^/|$baseurl/|" /tmp/$$.list

    cd $directory;
   
    while read filename;
    do
        curl -s -O "$baseurl/$filename" 
        echo "$baseurl/$filename" 
    done < /tmp/$$.list


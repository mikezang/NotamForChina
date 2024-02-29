#!/bin/bash 
#Filename: webtracking.sh
#Desc: Tracking web site if changed

folder=WebSiteTracking
today=today.html
amoad=AMoAd.html
medibaad=MedibaAd.html
adlantis=AdLantis.html

username1=mikezang
username2=mikezang@yahoo.co.jp
password=Zyf950824

lastmodified="Last-Modified:"
contentlength="Content-Length:"

if [ $# -lt 2 ]; then
    echo -e "$Usage $0 URL -o filename -s -d\n"
    exit -1
fi

first_time=0
size=0
download=0

for i in {1..5} 
do
    case $1 in
        -o) shift; outfile=$1; shift;;
        -s) shift; size=1; shift;;
        -d) shift; download=1; shift;;
        *) url=${url:-$1}; shift;;
    esac
done

if [ ! -e "$folder/$outfile" ]; then
    first_time=1
fi

if [ "$outfile" = "$amoad" ]; then
    username=$username1
elif [ "$outfile" = "$medibaad" ]; then 
    username=$username2
else
    usename="" 
fi

if [ "$outfile" = "$amoad" -o "$outfile" = "$medibaad" ]; then
    result=$(curl -u $username:$password -I --silent $url | grep $lastmodified)
else
    result=$(curl -I --silent $url | grep $lastmodified)
fi

if [[ -z $result ]]; then
    if [ "$outfile" = "$amoad" -o "$outfile" = "$medibaad" ]; then
        result=$(curl -u $username:$password -I --silent $url | grep $contentlength)
    else
        result=$(curl -I --silent $url | grep $contentlength)
    fi

    echo ${result} > /tmp/$today
else
    echo ${result:0:31} > /tmp/$today
fi

urlFilename=$(basename $url)

if [ $first_time -ne 1 ]; then
    changes=$(diff -u $folder/$outfile /tmp/$today)

    if [ -n "$changes" ]; then
        echo -e "[$urlFilename] Changed:\n"
        echo "$changes"

	if [ $download = "1" ]; then
            if [ "$outfile" = "$amoad" -o "$outfile" = "$medibaad" ]; then
        	curl -u $username:$password --silent $url -O
    	    else
        	curl --silent $url -O
            fi

	    echo " " | mail -s "Downloaded new $urlFilename" mikezang2008@gmail.com
	fi
    else
        echo -e "[$urlFilename] has no changes"
    fi
else
    echo "[$urlFilename] First run..."
fi

cp /tmp/$today $folder/$outfile

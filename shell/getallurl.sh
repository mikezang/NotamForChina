wget --spider --recursive --no-verbose --output-file=wgetlog.txt $1
sed -n "s@.\+ URL:\([^ ]\+\) .\+@\1@p" wgetlog.txt | sed "s@&@\&amp;@" > sedlog.txt


#wget --spider --force-html -r -l2 $1 2>&1 \
#  | grep '^--' | awk '{ print $3 }' \
#  | grep -v '\.\(css\|js\|png\|gif\|jpg\)$' \
#  > urls.m3u

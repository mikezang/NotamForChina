#awk 'NR==FNR{if (!/^\/\*/) A[$1]=$3; next} $1 in A && !/^\/\*/{$3=A[$1]}1' old-utf8.txt new-utf8.txt
#awk 'NR==FNR{if (!/^\/\*/) A[$1]=$3; next} ' old-utf8.txt new-utf8.txt
awk 'NR==FNR&&/^\/\*/{x=$0;getline;a[x]=$0;next}/^\/\*/{x=$0;print;getline;$0=a[x]?a[x]:$0;printf $0"\n\n"}' old-utf8.txt new-utf8.txt

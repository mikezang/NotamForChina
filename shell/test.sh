#!/bin/sh

newFilename=$1
oldFilename=$2

echo $newFilename
echo $oldFilename

awk '
  BEGIN { 
    while ( (getline var < ARGV[1]) > 0) { 
      data[var]++ 
    } 
  } 
  {  print $0 }
' "$oldFilename" "$newFilename"

exit

#awk 'NR==FNR&&/^\/\*/{x=$0;getline;a[x]=$0;next}/^\/\*/{x=$0;print;getline;$0=a[x]?a[x]:$0;printf $0"\n\n"}' $1 $2

for storyboardPath in `find . -name "*.storyboard" -print`
#for storyboardPath in `find "${PROJECT_DIR}" -name "*.storyboard" -print`
do
  storyboardFile=$(basename "$storyboardPath")
  baseStringsPath=$(echo "$storyboardPath" | sed 's/storyboard/strings/g')
  stringsFile=$(basename "$baseStringsPath")

  echo Create $stringsFile from $storyboardFile
  ibtool --export-strings-file $baseStringsPath $storyboardPath

  #for localeStringsPath in `find "${PROJECT_DIR}" -name "$stringsFile" -print`
  for localeStringsPath in `find . -name "$stringsFile" -print`
  do
    if [ $baseStringsPath != $localeStringsPath ]
    then
      echo Merge $baseStringsPath to $localeStringsPath
      awk 'NR==FNR{if (!/^\/\*/) A[$1]=$3; next} $1 in A && !/^\/\*/{$3=A[$1]}' "$localeStringsPath" "$baseStringsPath" 
      awk 'NR==FNR&&/^\/\*/{x=$0;getline;a[x]=$0;next}/^\/\*/{x=$0;print;getline;$0=a[x]?a[x]:$0;printf $0"\n\n"}' "$localeStringsPath" "$baseStringsPath"
    fi
  done
done


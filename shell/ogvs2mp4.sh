if [ -z "$1" ]; then
  echo Usage: ogvs2mp4.sh ogvFilenameSubstring 
  echo Convert ogv file to mp4 by ffmpeg
  exit
fi

ogvFiles="*$1*.ogv"
i=0

for ogvFile in $ogvFiles; do
  if [ -f "$ogvFile" ]; then
    mp4File="${ogvFile%.ogv}.mp4"

    printf "convert $ogvFile\nto      $mp4File\n"
    ffmpeg -i $ogvFile -y $mp4File
    let i++
  fi
done
 
if [ $i -eq 0 ]; then
  echo Usage: ogvs2mp4.sh ogvFilenameSubstring 
  echo Convert ogv file to mp4 by ffmpeg
  echo "The "$ogvFiles" file not found!" 
fi

exit


if [[ -z "$1" ]]; then
  echo Usage: mergemp4.sh videoFilesSubstring
  echo Merge video files to one video file
  exit
fi

gameCoverVideo="/Volumes/HD250GB/SpaceChem/SpaceChem-cover-music.mp4"
videoFiles=*$1*.mp4

echo -n > list.txt
#echo "file /Volumes/HD250GB/SpaceChem/SpaceChem-cover-music.mp4" >> list.file

for videoFile in $videoFiles; do 
  #if [[ $videoFile != *-Solutions.mp4 ]]; then
  if [[ $videoFile == *-music.mp4 ]]; then
    if [[ $videoFile == *-cover-music.mp4 ]]; then
      issueCoverVideo=$videoFile
      outVideoFile=${issueCoverVideo//cover-music/Solutions}
    else
      echo "file $videoFile" >> list.txt
    fi

  fi
done

echo "file $issueCoverVideo" | cat - list.txt > temp && mv temp list.txt
echo "file $gameCoverVideo" | cat - list.txt > temp && mv temp list.txt

printf "Merge files\n"
cat list.txt
echo "  to $outVideoFile"

ffmpeg -safe 0 -f concat -i list.txt -c copy -y $outVideoFile

rm list.txt

if [ $# -eq 0 ]; then
  echo Usage: addcover.sh imageFilename 
  echo Add Cover image to Video
  echo no file extension
  exit
fi

basename=$(basename "$1" .jpg)
imageFile="$basename.jpg"

videoFile=/Volumes/HD250GB/SpaceChem/SpaceChem-cover-music.mp4
videoCoverFile=$basename-cover-music.mp4

if [[ ! -f $videoFile ]]; then
  echo Usage: addcover.sh imageFilename videoFilename 
  echo Add Cover image to Video
  echo video $videoFile not found!
  exit
fi 

if [[ ! -f $imageFile ]]; then
  echo Usage: addcover.sh imageFilename videoFilename 
  echo Add Cover image to Video
  echo image $imageFile not found!
  exit
fi 

printf "Convert $imageFile\n"
printf "& music $videoFile\n" 
printf "     to $videoCoverFile\n"

#ffmpeg -loop 1 -i $videoFile -i $imageFile -t 3 $videoCoverFile
ffmpeg -i $videoFile -i $imageFile -filter_complex "[0:v][1:v] overlay=0:0" -c:a copy -shortest -t 5 -y $videoCoverFile 


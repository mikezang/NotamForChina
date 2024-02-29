if [ -z "$2" ]; then
  echo Usage: addmp32mp4.sh mp4FilenameString mp3FilenameSubtring
  echo Add mp3 music to mp4 video
  exit
fi

musicPath=/Volumes/HD250GB/Music/山口百恵/
mp4Files=*$1*.mp4
mp3Files=*$2*.mp3

for mp3File in $musicPath$mp3Files; do 
  if [ -f $mp3File ]; then
    #echo $mp3File
    musicArray=("${musicArray[@]}" "$mp3File")
  else
    echo Usage: addmp32mp4.sh mp4FilenameString mp3FilenameSubtring
    echo Add mp3 music to mp4 video
    echo $musicPath$mp3Files not found!
    exit
  fi
done

i=0
#musicCount=${#musicArray[@]}

for mp4File in $mp4Files; do
  if [[ -f $mp4File ]]; then
    if [[ $mp4File != *-music.mp4 ]] && [[ $mp4File != *s.mp4 ]]; then
      mp3File=${musicArray[$i]}

      if [ "$mp3File" == "" ]; then
        mp3File=${musicArray[0]}
      fi
 
      mp4MusicFile="${mp4File%.*}"-music.mp4
      printf "Add ${mp3File}\n to $mp4File\n as $mp4MusicFile\n"
      ffmpeg -i $mp4File -i ${mp3File} -c copy -shortest -map 0:v -map 1:a -y $mp4MusicFile
      let i++
    fi
  else
    echo Usage: addmp32mp4.sh mp4FilenameString mp3FilenameSubtring
    echo Add mp3 music to mp4 video
    echo $mp4File not found!
    exit
  fi
done

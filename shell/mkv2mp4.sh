if [ -z "$1" ]; then
  echo Usage: mkv2mp4.sh infile [outfile]
elif [ -z "$2" ]; then
  /Applications/ffmpeg -i $1.mkv -vcodec h264 -acodec mp2 $1.mp4
else
  /Applications/ffmpeg -i $1.mkv -vcodec h264 -acodec mp2 $2.mp4
fi

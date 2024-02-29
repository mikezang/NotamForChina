if [ -z "$1" ]; then
  echo Usage: avi2mp4.sh infile [outfile]
elif [ -z "$2" ]; then
  ffmpeg -i $1.avi -c:a copy -y $1.mp4
else
  ffmpeg -i $1.avi -c:a copy -y $2.mp4
fi

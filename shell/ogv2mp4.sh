if [ -z "$2" ] && [ -f "$1.ogv" ]; then
  ffmpeg -i $1.ogv -y $1.mp4
#  rm $1.gov
elif [ -f "$1.ogv" ]; then
  ffmpeg -i $1.ogv -y $2.mp4
#  rm $1.gov
else
  echo Usage: ogv2mp4.sh infile [outfile]
fi 

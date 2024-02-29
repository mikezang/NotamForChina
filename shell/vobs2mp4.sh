if [ -z "$1" ]; then
  echo Usage: vobs2mp4.sh infile_Prefix [outfile]
elif [ -z "$2" ]; then
  /Applications/ffmpeg -i "concat:VTS_$1_0.VOB|VTS_$1_1.VOB|VTS_$1_2.VOB|VTS_$1_3.VOB|VTS_$1_4.VOB|VTS_$1_5.VOB" -vcodec h264 -acodec mp2 $1.mp4
else
  /Applications/ffmpeg -i "concat:VTS_$1_0.VOB|VTS_$1_1.VOB|VTS_$1_2.VOB|VTS_$1_3.VOB|VTS_$1_4.VOB|VTS_$1_5.VOB" -vcodec h264 -acodec mp2 $2.mp4
fi

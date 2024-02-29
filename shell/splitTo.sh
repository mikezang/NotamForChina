if [ -z $3 ]; then
  echo "Split video file with soecific duration"
  echo "Usage: %0 oldFilenameExt toTimeSeconds newFilenameExt"
  echo "oldFilenameExt: Old video Filename with extension"
  echo "newFilenameExt: New video Filename with extension"
  exit
fi


ffmpeg -i %1 -t %2 -c copy %3



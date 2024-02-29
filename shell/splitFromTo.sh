if [ -z $4 ]; then
  echo "Split video file from soecific time to specific time
  echo "Usage: %0 oldFilenameExt fromTimeSeconds toTimeHH:MM:SS newFilenameExt
  echo "oldFilenameExt: Old video Filename with extension
  echo "newFilenameExt: New video Filename with extension
  exit
fi

ffmpeg -i %1 -ss %2 -to %3 -c copy %4


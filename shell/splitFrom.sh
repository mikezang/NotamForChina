if [ -z "$3" ]; then
  echo "Extract video file from soecific time"
  echo "Usage: $0 oldFilenameExt fromTimeSeconds newFilenameExt"
  echo " oldFilenameExt: Old video Filename with extension"
  echo "fromTimeSeconds: Extract from seconds"
  echo " newFilenameExt: New video Filename with extension"
  exit
fi

ffmpeg -i $1 -ss $2 -c copy $3

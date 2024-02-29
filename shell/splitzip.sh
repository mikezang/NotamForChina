if [ -z "$1" ]; then
  echo Usage: splitzip.sh folder zipfile
elif [ -z "$2" ]; then
  zip -r -s 500m $1.zip $1/
else
  zip -r -s 500m $2.zip $1/
fi 

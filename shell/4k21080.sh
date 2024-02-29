ffmpeg -i $1 -vf scale=1920:-1 -metadata Title="$2" $2

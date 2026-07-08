album_artist="$(basename "$(dirname "$PWD")")"

find . -type f \( -iname "*.m4a" -o -iname "*.mp4" \) | while read -r f; do
  album="$(basename $PWD)"
  title="$(basename "${f%.*}")"

  AtomicParsley "$f" \
    --artist "" \
    --composer "" \
    --albumArtist "$album_artist" \
    --album "$album" \
    --title "$title" \
    --compilation no \
    --overWrite

  echo 
  echo "ablum_artist: $album_artist"
  echo "album: $album"
  echo "title: $title"
done


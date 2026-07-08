album_artist="$(basename "$PWD")"

find . -type f \( -iname "*.m4a" -o -iname "*.mp4" \) | while read -r f; do
  album="$(basename "$(dirname "$f")")"
  title="$(basename "${f%.*}")"

  AtomicParsley "$f" \
    --artist "" \
    --composer "" \
    --albumArtist "$album_artist" \
    --album "$album" \
    --title "$title" \
    --compilation no \
    --overWrite
done


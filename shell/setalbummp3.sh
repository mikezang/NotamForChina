album_artist="$(basename "$PWD")"

find . -type f -iname "*.mp3" | while read -r f; do
  album="$(basename "$(dirname "$f")")"
  title="$(basename "${f%.*}")"

  eyeD3 \
    --remove-all \
    --album-artist "$album_artist" \
    --album "$album" \
    --title "$title" \
    "$f"
done

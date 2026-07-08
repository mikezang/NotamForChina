find . -type d -name "*" | while read -r dir; do
  cover="$dir/cover.png"
  [ -f "$cover" ] || continue

  for mp3 in "$dir"/*.mp3; do
    [ -f "$mp3" ] || continue
    eyeD3 \
      --remove-all-images \
      --add-image "$cover:FRONT_COVER" \
      "$mp3"
  done
done

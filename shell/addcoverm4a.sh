find . -type d -name "*" | while read -r dir; do
  # find cover
  if [ -f "$dir/cover.jpg" ]; then
    cover="$dir/cover.jpg"
  elif [ -f "$dir/cover.png" ]; then
    cover="$dir/cover.png"
  else
    echo "⚠️  No cover, skip: $FILE"
    continue 
  fi

  [ -f "$cover" ] || continue

  for m4a in "$dir"/*.m4a; do
    [ -f "$m4a" ] || continue
    AtomicParsley "$m4a" \
      --artwork REMOVE_ALL \
      --artwork "$cover" \
      --overWrite
  done
done

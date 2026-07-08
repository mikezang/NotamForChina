# find cover
if [ -f "cover.jpg" ]; then
  cover="cover.jpg"
elif [ -f "cover.png" ]; then
  cover="cover.png"
else
  echo "⚠️  No cover, skip"
fi

[ -f "$cover" ] || exit

for m4a in *.m4a; do
  [ -f "$m4a" ] || continue
  AtomicParsley "$m4a" \
    --artwork REMOVE_ALL \
    --artwork "$cover" \
    --overWrite
done

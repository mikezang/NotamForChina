#!/bin/bash
set -e

ROOT_DIR="$(pwd)"
ALBUM_ARTIST="$(basename "$ROOT_DIR")"

echo "Album Artist (main folder): $ALBUM_ARTIST"
echo "========================================"

find . -type f \( -iname "*.mp3" -o -iname "*.m4a" \) | while read -r FILE; do

  DIR="$(dirname "$FILE")"
  ALBUM="$(basename "$DIR")"
  TITLE="$(basename "${FILE%.*}")"

  # find cover
  if [ -f "$DIR/cover.jpg" ]; then
    COVER="$DIR/cover.jpg"
  elif [ -f "$DIR/cover.png" ]; then
    COVER="$DIR/cover.png"
  else
    echo "⚠️  No cover, skip: $FILE"
    continue
  fi

  EXT="${FILE##*.}"

  # ---------- SKIP IF ALREADY CORRECT ----------
  case "$EXT" in
    mp3|MP3)
      CUR_TITLE=$(eyeD3 --no-color "$FILE" | sed -n 's/^title: //p')
      CUR_ALBUM=$(eyeD3 --no-color "$FILE" | sed -n 's/^album: //p')
      CUR_ALBUM_ARTIST=$(eyeD3 --no-color "$FILE" | sed -n 's/^album artist: //p')

      if [[ "$CUR_TITLE" == "$TITLE" &&
            "$CUR_ALBUM" == "$ALBUM" &&
            "$CUR_ALBUM_ARTIST" == "$ALBUM_ARTIST" ]]; then
        echo "✔ already tagged, skip: $FILE"
        continue
      fi
      ;;
    m4a|M4A)
      CUR_TITLE=$(AtomicParsley "$FILE" -t | sed -n 's/^Title: //p')
      CUR_ALBUM=$(AtomicParsley "$FILE" -t | sed -n 's/^Album: //p')
      CUR_ALBUM_ARTIST=$(AtomicParsley "$FILE" -t | sed -n 's/^Album Artist: //p')

      if [[ "$CUR_TITLE" == "$TITLE" &&
            "$CUR_ALBUM" == "$ALBUM" &&
            "$CUR_ALBUM_ARTIST" == "$ALBUM_ARTIST" ]]; then
        echo "✔ already tagged, skip: $FILE"
        continue
      fi
      ;;
  esac

  echo "✎ tagging: $FILE"

  # ---------- TAGGING ----------
  case "$EXT" in
    mp3|MP3)
      eyeD3 \
        --remove-all-images \
        --remove-frame TALB \
        --remove-frame TPE2 \
        --remove-frame TPE1 \
        --remove-frame TCOM \
        --title "$TITLE" \
        --album "$ALBUM" \
        --album-artist "$ALBUM_ARTIST" \
        --add-image "$COVER:FRONT_COVER" \
        "$FILE"
      ;;
    m4a|M4A)
      AtomicParsley "$FILE" \
        --title "" \
        --album "" \
        --artist "" \
        --albumArtist "" \
        --composer "" \
        --title "$TITLE" \
        --album "$ALBUM" \
        --albumArtist "$ALBUM_ARTIST" \
        --artwork "$COVER" \
        --overWrite
      ;;
  esac

done

echo
echo "All done ✔"


for file in *.jpg; do
  convert "$file" -rotate 90 ../"$file"
done

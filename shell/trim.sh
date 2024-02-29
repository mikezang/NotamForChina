function trim() {
  for f in . *.$1; do
    case $f in
      *\ *) 
        g="${f// /}"
        h="${g//)/}"
        i="${h//,/-}"
        j="${i//\(/-}"
        printf "rename $f to $j\n"
        mv "$f" "$j"  
    esac
  done
}

# current folder
#trim jpg
#trim ogv

# ~/Desktop folder
#cd ~/Desktop
#trim ogv

# ~/Sicreenshots folder
pushd ~/Screenshots
trim png
trim jpg


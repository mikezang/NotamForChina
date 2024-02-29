: '
 This script is to rename SpaceChem Screnn shot image file and move to rlevant folder
'

#trim.sh

if [[ -z "$4" ]]; then
   echo Usage: renjpg.sh oldJpgFilename volume issueNo issueName
   exit
fi
 
#cd ~/Desktop/Snapshot
filename=$(basename $1 .jpg)
filename="$filename.jpg"

for oldFilename in $filename; do
  issueNo=${3:0:7}
  echo $issueNo
  newFilename="/Volumes/HD250GB/SpaceChem/ResearchNet/$2/$issueNo/SpaceChem-ResearchNet-$2-$3-$4.jpg"
  echo "move $oldFilename"
  echo "  to $newFilename"
  mv $oldFilename $newFilename
done

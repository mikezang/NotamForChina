GROUP="$(diskutil info $1 | grep "APFS Volume Group")"
UUID="${GROUP##* }"
echo $UUID

# Boot name in folder as below
# Sonoma(/dev/disk1s2): /System/Volumes/Preboot/6EA8916B-8A05-4AE9-A30F-8D0C81A5138E/System/Library/CoreServices
# Monterey(/dev/disk4s2): /Volumes/Preboot/E6F45525-AAD7-44DB-A9EC-55DC3F4A89CD/System/Library/CoreServices

# echo cd /System/Volumes/Preboot/$UUID/System/Library/CoreServices/
# echo sudo bless --folder . --label "Macintosh HD"
# echo printf "Macintosh HD" | sudo tee .disk_label.contentDetails; echo
# sudo chgrp wheel .disk*
#cd ~


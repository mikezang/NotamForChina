#softwareupdate --list
sudo rm -rf /Library/Preferences/com.apple.SoftwareUpdate.plist
sudo rm -rf /Library/Preferences/com.apple.SoftwareUpdate*
sudo rm -rf /private/var/db/softwareupdate/*
sudo rm -rf /private/var/db/receipts/*
echo PLEASE SHUTDOWN NOT REBOOT

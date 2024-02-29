#!/bin/bash

diskutil erasevolume HFS+ 'JDKRAMDISK'  `hdiutil attach -nomount ram://3072000`
sudo cp -r /Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home /Volumes/JDKRAMDISK
sudo cp -r /Applications/sts-bundle/sts.app /Volumes/JDKRAMDISK


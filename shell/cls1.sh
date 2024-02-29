#!/bin/sh
# cls.sh - script to  Create Locale Strings auto

storyboardExt=".storyboard"
stringsExt=".strings"
newStringsExt=".strings.new"
oldStringsExt=".strings.old"
localeDirExt=".lproj"
baseLprojDir="Base${localeDirExt}"

iPadStoryboardStringsFile=""
iPhoneStoryboardStringsFile=""
localizableStringsFile="Localizable.strings"
infoPlistStringsFile="InfoPlist.strings"
rootStringsFile="Root.strings"

indexPadStoryboardStrings=0
indexPhoneStoryboardStrings=1
indexLocalizableStrings=2
indexInfoPlistStrings=3
indexRootStrings=4

index=0

echo "${baseLprojDir}"

# Find Base.lproj path
baseLprojPath=`find . -name "${baseLprojDir}" -print`
echo "baseLprojPath= ${baseLprojPath}"

#Find storyboard file full path inside project folder
for storyboardPath in `find "${baseLprojPath}" -name "*${storyboardExt}" -print`
do
    echo "storyboardPath= ${storyboardPath}"

    # Get Base strings file path
    baseStoryboardStringsPath=$(echo "$storyboardPath" | sed "s/$storyboardExt/$stringsExt/")
    echo "baseStoryboardStringsPath= ${baseStoryboardStringsPath}"

    if [ $index = 0 ]; then
    	iPadStoryboardStringsFile=$(basename "$baseStoryboardStringsPath")
    	echo "iPadStoryboardStringsFile= ${iPadStoryboardStringsFile}"
    else
    	iPhoneStoryboardStringsFile=$(basename "$baseStoryboardStringsPath")
    	echo "iPhoneStoryboardStringsFile= ${iPhoneStoryboardStringsFile}"
    fi

    baseStringsArray[$index]="${baseStoryboardStringsPath}"
    echo "${baseStringsArray[$index]}"
    index=$index+1;
done

baseStringsArray[$index]="${baseLprojPath}/${localizableStringsFile}"
index=$index+1;
baseStringsArray[$index]="${baseLprojPath}/${infoPlistStringsFile}"
index=$index+1;
baseStringsArray[$index]="${baseLprojPath}/${rootStringsFile}"

for index in "${!baseStringsArray[@]}"
do
    echo "baseStringsArray[$index]= ${baseStringsArray[$index]}"
done

# Find iPadStoryboard.strings
for iPadStoryboardStringsPath in `find . -name "${iPadStoryboardStringsFile}" -print`
do
    if [ ${iPadStoryboardStringsPath} != ${baseStringsArray[$indexPadStoryboardStrings]} ]; then
        echo "${iPadStoryboardStringsPath}"
    fi
done

# Find iPihoneStoryboard.strings
for iPhoneStoryboardStringsPath in `find . -name "${iPhoneStoryboardStringsFile}" -print`
do
    if [ ${iPhoneStoryboardStringsPath} != ${baseStringsArray[$indexPhoneStoryboardStrings]} ]; then
        echo "${iPhoneStoryboardStringsPath}"
    fi
done

# Find Localizable.strings
for localizableStringsPath in `find . -name "${localizableStringsFile}" -print`
do
    if [ ${localizableStringsPath} != ${baseStringsArray[$indexLocalizableStrings]} ]; then
        echo "${localizableStringsPath}"
    fi
done

# Find InfoPlist.strings
for infoPlistStringsPath in `find . -name "${infoPlistStringsFile}" -print`
do
    if [ ${infoPlistStringsPath} != ${baseStringsArray[$indexInfoPlistStrings]} ]; then
        echo "${infoPlistStringsPath}"
    fi
done

# Find Root.strings
for rootStringsPath in `find . -name "${rootStringsFile}" -print`
do
    if [ ${rootStringsPath} != ${baseStringsArray[$indexRootStrings]} ]; then
        echo "${rootStringsPath}"
    fi
done






exit

# Find storyboard file full path inside project folder
for storyboardPath in `find . -name "*$storyboardExt" -print`
do
  	# Get Base strings file full path
  	baseStringsPath=$(echo "$storyboardPath" | sed "s/$storyboardExt/$stringsExt/")

	echo "storyboard path: $storyboardPath"
	echo "base strings path: $baseStringsPath"

	# Create strings file only when storyboard file newer
	if find $storyboardPath -prune -newer $baseStringsPath -print | grep -q .; then
  		# Get storyboard file name and folder 
  		storyboardFile=$(basename "$storyboardPath")
  		storyboardDir=$(dirname "$storyboardPath")

		echo "storyboard folder: $storyboardDir"
		echo "storyboard file: $storyboardFile"

  		# Get New Base strings file full path and strings file name
  		newBaseStringsPath=$(echo "$storyboardPath" | sed "s/$storyboardExt/$newStringsExt/")
  		stringsFile=$(basename "$baseStringsPath")

		echo "new base strings path: $newBaseStringsPath"
		echo "strings file: $stringsFile"

  		echo "Create $newBaseStringsPath from $storyboardFile"
  		ibtool --export-strings-file $newBaseStringsPath $storyboardPath

  		# Convert UTF-16 to UTF-8
  		iconv -f UTF-16 -t UTF-8 $newBaseStringsPath > $baseStringsPath

		# Remove UTF-16 strings file
		rm $newBaseStringsPath

  		# Get all locale strings folder 
  		for localeStringsDir in `find . -name "*$localeDirExt" -print`
  		do
			echo "localeStringsDir: $localeStringsDir"

			# Skip Base strings folder
            if [ $localeStringsDir != $storyboardDir ]; then
				localeStringsPath=$localeStringsDir/$stringsFile
				echo "locale strings path: $localeStringsPath"

				# Just copy base strings file on first time
				if [ ! -e $localeStringsPath ]; then
					cp $baseStringsPath $localeStringsPath
				else
                    oldLocaleStringsPath=$(echo "$localeStringsPath" | sed "s/$stringsExt/$oldStringsExt/")

					echo "old locale strings path: $oldLocaleStringsPath"
      				cp $localeStringsPath $oldLocaleStringsPath

      				echo "Merge $baseStringsPath to $localeStringsPath"
            		awk 'NR == FNR && /^\/\*/ {x=$0; getline; a[x]=$0; next} /^\/\*/ {x=$0; print; getline; $0=a[x]?a[x]:$0; printf $0"\n\n"}' $oldLocaleStringsPath $baseStringsPath > $localeStringsPath

					# Remove old locale strings file
					rm $oldLocaleStringsPath
                fi
			fi
  		done
	else
		echo "$storyboardPath file not modified."
	fi
done

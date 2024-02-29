: '
 This script to remove all spaces in SpaceChem solution video name from
SpaceChem How Ionic (959, 1, 60) 2023-02-24-14-44-17.ogv
SpaceChem How Ionic (968, 1, 59) 2023-02-24-14-24-10.ogv
SpaceChem How Ionic (979, 1, 58) 2023-02-24-14-34-41.ogv
SpaceChem How Ionic (1268, 1 ,64) 2023-02-24-13-35-48.ogv
SpaceChem How Ionic (1295, 1 ,63) 2023-02-24-14-39-34.ogv

to 
SpaceChem-HowIonic(959,1,60)-2023-02-24-14-44-17.ogv
SpaceChem-HowIonic(968,1,59)-2023-02-24-14-24-10.ogv
SpaceChem-HowIonic(979,1,58)-2023-02-24-14-34-41.ogv
SpaceChem-HowIonic(1268,1,64)-2023-02-24-13-35-48.ogv
SpaceChem-HowIonic(1295,1,63)-2023-02-24-14-39-34.ogv

then rename to
SpaceChem-ResearchNet-Volume8-Issue10-HowIonic-Solution1-1295-1-63.ogv
SpaceChem-ResearchNet-Volume8-Issue10-HowIonic-Solution2-1268-1-64.ogv
SpaceChem-ResearchNet-Volume8-Issue10-HowIonic-Solution3-0979-1-58.ogv
SpaceChem-ResearchNet-Volume8-Issue10-HowIonic-Solution4-0968-1-59.ogv
SpaceChem-ResearchNet-Volume8-Issue10-HowIonic-Solution5-0959-1-60.ogv
 
'

dataFile=/Volumes/HD250GB/SpaceChem/SpaceChem.csv

function indexOf() {
  echo "$1" "$2" | awk '{print index($1, $2)}'
}

function indexOfAfter() {
   echo "$1" "$2" "$3" | awk '{s=substr($2, $1);posn=index(s,$3);if (posn>0) print $1+posn-1; else print 0;}'
}

# move files to work folder
#mvfiles.sh

# Remove all spaces in all filenames
trim.sh $newPath

# show usage if no any paramerters
if [ -z "$1" ]; then
  echo 'Usage: renogvs.sh keyword(issue name)'
  echo Rename ogv files
  exit
fi

keyword=$1

# find all renamed .ogv files with specific keyword (issue name)
for filenameExt in *$keyword-Solution*.ogv; do
  if [ -f "$filenameExt" ]; then           # if file exists
    #if [[ "$filenameExt" != *ResearchNet* ]]; then # exclude file if include "ResearchNet"
    oldFileArray+=(${filenameExt})       # add old filename to array
    #fi
  else 
    echo 'Usage: renogvs.sh keyword(issue name)'
    echo Rename ogv files
    echo *$keyword-Solution*.ogv files not found!
    exit
  fi
done

# rename sorted filename to original format
for oldFile in ${oldFileArray[@]}; do
  IFS='-' read -r -a nameArray <<< "$oldFile" # split filename to array by delemiter '-'
  spaceChem=${nameArray[0]}   # SpaceChema constant
  reaserchNet=${nameArray[1]} # ResearchNet constant
  volume=${nameArray[2]}      # Volume
  issueNo=${nameArray[3]}     # Issue No
  issueName=${nameArray[4]}   # Issue Name
  solutionNo=${nameArray[5]}  # Solution No
  cycle=${nameArray[6]}       # Cycle
  symbol=${nameArray[7]}      # Symbol
  reactor=${nameArray[8]}     # Reactor.ogv
  #printf "%s\n" ${nameArray[@]}

  newFile="$spaceChem-$issueName-$cycle-$symbol-$reactor"
  echo "move $oldFile"
  echo "  to $newFile"
  mv $oldFile $newFile
done

# find all .ogv files with specific keyword (issue name)
for filenameExt in *$keyword-*.ogv; do
  if [ -f "$filenameExt" ]; then           # if file exists
    if [[ "$filenameExt" != *ResearchNet* ]]; then # exclude file if include "ResearchNet"
      oldFileArrayTemp1+=(${filenameExt})       # add old filename to array
    fi
  else 
    echo 'Usage: renogvs.sh keyword(issue name)'
    echo Rename ogv files
    echo *$keyword-*.ogv files not found!
    exit
  fi
done

# Sort the new filenames
oldFileArray=$(printf "%s\n" ${oldFileArrayTemp1[@]} | sort -t- -k3nr -k4nr -k5nr) 

printf "%s\n" ${oldFileArray[@]} 
printf "%s\n" ${oldFileArray[0]} 
printf "%s\n" ${oldFileArray[1]} 
printf "%s\n" ${oldFileArray[2]} 
printf "%s\n" ${oldFileArray[3]} 
printf "%s\n" ${oldFileArray[4]} 
printf "%s\n" ${oldFileArray[5]} 
#printf "%s\n" ${newFileArray[@]} 

exit

solutionNo=1

# move old file to relevant folder with new filename 
for oldFilename in ${oldFileArray[@]}; do
  #filename="${filenameExt%.*}"         # Get filename without extension
  IFS='-' read -r -a nameArray <<< "$oldFilename" # split filename to array by delemiter '-'
  issueName=${nameArray[1]} # Issue Name
  cycle=${nameArray[2]}     # Cycle
  symbol=${nameArray[3]}    # Symbol
  reactor=${nameArray[4]}   # Reactor.ogv
  #printf "%s\n" ${nameArray[@]}
       
  # Find Volume, Issue no and column no by keyword (issue name) 
  #volumeissueNo=$(awk -F ',' -v var="$keyword" '$3==var || $4==var || $5==var {print $1, $2}' $dataFile)
  #read volume issueNo <<< $(awk -F ',' -v var="$keyword" '$3==var || $4==var || $5==var {print $1, $2}' $dataFile)
  read volume issueNo colNo <<< $(awk -F ',' -v var="$keyword" '{
    if ($3==var) {col=1}
    if ($4==var) {col=2} 
    if ($5==var) {col=3}
    if ($6==var) {col=4}
    if ($7==var) {col=5}
    if ($8==var) {col=6}
    if (col) {print $1, $2, col; exit}
  }' $dataFile)

  #echo  Volume: $volume
  #echo IssueNo: $issueNo
  #echo  column: $colNo

  # exit if no keyword in csv file
  if [[ "$volume" == "" ]] || [[ "$issueNo" == "" ]]; then
    echo $keyword not founnd in $dataFile
    exit
  fi

  # exit if multiple results 
  temp=($issueNo)

  if [[ ${#temp[@]} > 1 ]]; then
    echo IssueNo has mutiples values: ${issueNo}
    exit
  fi
  
  # check if ResearchNet
  if [[ "$vlume" == "Volume" ]]; then
    # make new filename
    printf -v number '%02d' $solutionNo # Padding 0 for two digits
    newPath="/Volumes/HD250GB/SpaceChem/ResearchNet/${volume}/${issueNo}/"
    newFilename="SpaceChem-ResearchNet-${volume}-${issueNo}${colNo}-${issueName}-Solution${number}-${cycle}-${symbol}-${reactor}.ogv"

    let solutionNo++
    lastSolutionNo=$solutionNo
  else
    colNo=$issueNo
    newPath="/Volumes/HD250GB/SpaceChem/${volume}/"

    #echo "      cycle: $cycle"
    #echo "  lastCycle: $lastCycle"
    #echo "     symbol: $symbol"
    #echo " lastSymbol: $lastSymbol"
    #echo "    reactor: $reactor"
    #echo "lastReactor: $lastReactor"

    # check if Production with Research with the same Cycles, Symbols and Reactors
    if [[ $cycle == $lastCycle ]] && [[ $symbol == $lastSymbol ]] && [[ $reactor == $lastReactor ]]; then
      printf -v number '%02d' $lastSolutionNo # Padding 0 for two digits
      newFilename="SpaceChem-${volume}${colNo}-${issueName}-Solution${number}-${cycle}-${symbol}-${reactor}-R$researchNo.ogv"
      let researchNo++
    else
      printf -v number '%02d' $solutionNo # Padding 0 for two digits
      newFilename="SpaceChem-${volume}${colNo}-${issueName}-Solution${number}-${cycle}-${symbol}-${reactor}.ogv"
      researchNo=1
      lastSolutionNo=$solutionNo
      let solutionNo++
    fi
  fi
 
  # check if Production with Research with the same Cycles, Symbols and Reactors
  #if [[ $cycle == $lastCycle ]] && [[ $symbol == $lastSymbol ]] && [[ $reactor == $lastReactor ]]; then
  #  printf -v number '%02d' $solutionNo # Padding 0 for two digits
  #  newPath="/Volumes/HD250GB/SpaceChem/${volume}/"
  #  newFilename="SpaceChem-ResearchNet-${volume}-${issueNo}${colNo}-${issueName}-Solution${number}-${cycle}-${symbol}-${reactor}-S{$researchNo}.ogv"
  #  
  #  let ResearchNo++
  #esle
    # make new filename
  #  printf -v number '%02d' $solutionNo # Padding 0 for two digits
  #  newPath="/Volumes/HD250GB/SpaceChem/ResearchNet/${volume}/${issueNo}/"
  #  newFilename="SpaceChem-ResearchNet-${volume}-${issueNo}${colNo}-${issueName}-Solution${number}-${cycle}-${symbol}-${reactor}.ogv"
  #
  #  let solutionNo++
  #  lastSolutionNo=1
  #fi

  lastCycle=$cycle
  lastSymbol=$symbol
  lastReactor=$reactor

  echo "Move $oldFilename"
  echo "  to $newPath$newFilename"

  #mv $oldFilename $newPath$newFilename     # rename then move to new folder

done



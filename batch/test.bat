if [%1] == [] goto :usage
echo %1

set x=%1
if [%x:~3,1%] == [.] (
   echo %x:~0,3%
) else (
   echo %x:~0,2%
)

goto :eof

echo %x%
echo %x:~0,3%
echo %x:~0,-2%
echo %x:~-2%

:usage
echo %0 float

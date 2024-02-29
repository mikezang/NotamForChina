
ffmpeg -i %1.mp4 -i %2.mp4 -filter_complex xfade=transition=slideleft:duration=5:offset=5 -y videos\output.mp4


rem ffmpeg -i %1.mp4 -i %2.mp4 -filter_complex "[0][1]xfade=transition=wipeleft:duration=5:offset=5" videos\output.mp4

rem * -filter_complex = … and starts a series of complex filters…
rem * xfade = … calling the xfade ffmpeg filter…
rem * transition= = … with the transition [TRANSITION_NAME] ... 
rem Note: Replace [TRANSITION_NAME] with the name of the transition you want. 
rem The transitions covered in the video are: fade, wipeleft, wiperight, wipeup, wipedown, 
rem slideleft, slideright, slideup, slidedown, circlecrop, rectcrop, distance, fadeblack, fadewhite, 
rem radial, smoothleft, smoothright, smoothup, smoothdown, circleopen, circleclose, vertopen, vertclose, 
rem horzopen, horzclose, dissolve, pixelize, diagtl, diagtr, diagbl, diagbr, hlslice, hrslice, vuslice, vdslice, hblur, 
rem fadegrays, wipetl, wipetr, wipebl, wipebr, squeezeh, squeezev
rem * duration=5 = ... for a transition duration of 5 seconds ...
rem * offset=2.5 = ... starting the transition after 2.5 seconds
rem * output.mp4 = … outputting the final result to file «output.mp4»

rem ffmpeg -i %1.mp4 -i %2.mp4 -filter_complex "[0][1]xfade=transition=slideleft:duration=5:offset=10,format=yuv420p" -y output.mp4

rem ffmpeg -loop 1 -t 5 -i 1.png -loop 1 -t 5 -i 2.png -filter_complex "[0][1]xfade=transition=fade:duration=1:offset=4,format=yuv420p" output.mp4

rem ffmpeg -i %1.mp4 -i %2.mp4 -f lavfi -i color=black -filter_complex "[0:v]fade=t=out:s=225:n=25:alpha=1,setpts=PTS-STARTPTS[va0];[1:v]fade=t=in:s=0:n=25:alpha=1,setpts=PTS-STARTPTS+4/TB[va1];[2:v]scale=1920x1080,trim=duration=9[over];[over][va0]overlay[over1];[over1][va1]overlay=format=yuv420[outv]" -vcodec libx264 -map [outv] -y videos\out.mp4


/Applications/VLC.app/Contents/MacOS/vlc $1 & sleep 0.4 \
&& osascript -e 'tell application "System Events"
    tell process "VLC"
        keystroke "m" using {command down, shift down}
        set size of window 1 to {640, 360}
        set position of window 1 to {100, 200}
    end tell
end tell'

#case "$1" in
#    *.mp4)
#        ffplay -x 321 -y 123 -af "volume=-20dB" $1
#	;;
#    *.ma4)
#        ffplay -x 321 -y 123 -af "volume=10dB" $1
#	;;
#    *)
#        ffplay -x 321 -y 123 -af "volume=-20dB" $1
#	;;
#esac


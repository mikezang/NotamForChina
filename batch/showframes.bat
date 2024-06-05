ffprobe -v 0 -select_streams v -show_entries stream=duration_ts,time_base,nb_frames %1

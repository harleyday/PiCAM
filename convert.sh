for i in *.h264; do
        # package the raw h264 file into an MP4, and remove the original .h264 file if the conversion was sucessful
        ffmpeg -r 30 -i "$i" -c copy "${i%.*}.MP4" && rm "$i"
done
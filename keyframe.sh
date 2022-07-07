for i in $@; do
ffprobe -show_frames -select_streams v -print_format json $i > ${i}.json
done
from moviepy.editor import VideoFileClip

# Input video file path
input_video_path = ""

# Output video file path
output_video_path = ""

# Define start and end times in hours, minutes, and seconds
start_time = (1 * 3600) + (42 * 60) + 42  # Convert 1:42:42 to seconds
end_time = (1 * 3600) + (44 * 60) + 12    # Convert 1:44:12 to seconds

# Load the video file
video = VideoFileClip(input_video_path)

# Trim the video using start and end times
clip = video.subclip(start_time, end_time)

# Write the clipped video to an output file
clip.write_videofile(output_video_path, codec="libx264", fps=video.fps)

# Close the video files
video.close()
clip.close()

print(f"Clipped video saved to {output_video_path}")

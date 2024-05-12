from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

def edit_video(video_path, image_path, output_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path).subclip(0,20)

    image_clip = ImageClip(image_path).set_start(0).set_duration(1).set_pos(("center","center"))
    image_clip2 = ImageClip(image_path).set_start(19).set_duration(1).set_pos(("center","center"))
    
    # Concatenate the image clip with the video clip
    final_clip = CompositeVideoClip([video_clip, image_clip, image_clip2])
    
    # Crop the final clip to have a 16:9 aspect ratio
    # final_clip = final_clip.resize(width=video_clip.size[0], height=video_clip.size[0] * 9 / 16)
    
    # Write the final clip to a file
    final_clip.write_videofile(output_path, fps=24, codec='libx264')
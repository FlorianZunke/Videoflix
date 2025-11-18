import subprocess




def convert_to_480p(video_path):
    cmd = f"ffmpeg -i {video_path} -vf scale=-2:480 {video_path.rsplit('.', 1)[0]}_480p.mp4"
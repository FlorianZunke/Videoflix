import subprocess


def convert_to_480p(video_path):
    cmd = f"ffmpeg -i {video_path} -vf scale=-2:480 {video_path.rsplit('.', 1)[0]}_480p.mp4"
    subprocess.run(cmd, shell=True)

def convert_to_360p(video_path):
    cmd = f"ffmpeg -i {video_path} -vf scale=-2:360 {video_path.rsplit('.', 1)[0]}_360p.mp4"
    subprocess.run(cmd, shell=True)

def convert_to_720p(video_path):
    cmd = f"ffmpeg -i {video_path} -vf scale=-2:720 {video_path.rsplit('.', 1)[0]}_720p.mp4"
    subprocess.run(cmd, shell=True)

def convert_to_1080p(video_path):
    cmd = f"ffmpeg -i {video_path} -vf scale=-2:1080 {video_path.rsplit('.', 1)[0]}_1080p.mp4"
    subprocess.run(cmd, shell=True)
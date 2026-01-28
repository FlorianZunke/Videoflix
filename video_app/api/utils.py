import os
import subprocess

from video_app.models import Video
from django.conf import settings


def convert_to_hls(video_id, video_path, resolution):
    output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id), f"{resolution}p")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "index.m3u8")
    
    cmd = (
        f"ffmpeg -i {video_path} -vf scale=-2:{resolution} "
        f"-start_number 0 -hls_time 10 -hls_list_size 0 -f hls {output_path}"
    )
    subprocess.run(cmd, shell=True, check=True)

def convert_and_save(video_id):
    from video_app.models import Video 
    
    try:
        video = Video.objects.get(id=video_id)
        source_path = video.video_file.path
        
        resolutions = [360, 480, 720, 1080]
        
        for res in resolutions:
            convert_to_hls(video_id, source_path, res)
            
        video.conversion_status = 'completed'
        
    except Exception as e:
        from video_app.models import Video
        video = Video.objects.filter(id=video_id).first()
        if video:
            video.conversion_status = 'failed'
            video.error_message = str(e)
    
    if video:
        video.save()
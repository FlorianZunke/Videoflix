import os
import subprocess

from django.conf import settings

def create_thumbnail(video_path, thumbnail_path):
    """
    Creates a thumbnail from the video using ffmpeg.
    This command takes a snapshot at 1 second into the video and saves it as a JPEG image.
    """
    cmd = f'ffmpeg -i "{video_path}" -ss 00:00:01 -vframes 1 "{thumbnail_path}" -y'
    subprocess.run(cmd, shell=True, check=True)

def convert_and_save(video_id):
    """
    Converts the video to HLS format, creates a thumbnail, and updates the conversion status in the database.
    """
    from video_app.models import Video 
    try:
        video = Video.objects.get(id=video_id)
        source_path = video.video_file.path
        
        thumb_name = f"thumb_{video.id}.jpg"
        thumb_rel_path = os.path.join('thumbnails', thumb_name)
        thumb_full_path = os.path.join(settings.MEDIA_ROOT, thumb_rel_path)
        
        os.makedirs(os.path.dirname(thumb_full_path), exist_ok=True)
        create_thumbnail(source_path, thumb_full_path)
        
        video.thumbnail_url = thumb_rel_path 
        video.save()

        resolutions = [480, 720, 1080]
        for res in resolutions:
            output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video.id), f"{res}p")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "index.m3u8")
            
            cmd = (
                f"ffmpeg -i {source_path} -vf scale=-2:{res} "
                f"-start_number 0 -hls_time 10 -hls_list_size 0 -f hls {output_path}"
            )
            subprocess.run(cmd, shell=True, check=True)
            
        video.conversion_status = 'completed'
        video.save()
        
    except Exception as e:
        print(f"Fehler: {e}")
        video.conversion_status = 'failed'
        video.save()

def convert_to_hls(video_id, video_path, resolution):
    """
    Converts a video to HLS format using ffmpeg and saves it to the specified output directory.
    """
    output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id), f"{resolution}p")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "index.m3u8")
    
    cmd = (
        f"ffmpeg -i {video_path} -vf scale=-2:{resolution} "
        f"-start_number 0 -hls_time 10 -hls_list_size 0 -f hls {output_path}"
    )
    subprocess.run(cmd, shell=True, check=True)
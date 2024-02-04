import hashlib
import os
import subprocess


def calculate_directory_hash(directory_path):
    sha256_hash = hashlib.sha256()

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def calculate_directory_size(directory_path):
    total_size = 0

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)

    return total_size


def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_video_length(video_path):
    return 1000


def should_generate_hls(mp4_path, m3u8_path):
    if not os.path.exists(m3u8_path):
        return True

    mp4_mtime = os.path.getmtime(mp4_path)
    m3u8_mtime = os.path.getmtime(m3u8_path)

    return mp4_mtime > m3u8_mtime


def generate_hls(videoname, quality):
    file_dir = os.path.dirname(os.path.abspath(__file__))
    videoname = os.path.normpath(videoname)
    hls_directory = os.path.join(file_dir, 'static', videoname)
    mp4_path = os.path.join(file_dir, videoname)

    quality_mapping = {
        720: (1280, 720),
        480: (640, 480),
        360: (480, 360),
        240: (426, 240),
        144: (256, 144)
    }

    if quality not in quality_mapping:
        raise ValueError("Invalid quality value")

    width, height = quality_mapping[quality]

    quality_dir = os.path.join(hls_directory, f"{quality}p")
    quality_m3u8 = os.path.join(quality_dir, 'hls.m3u8')

    os.makedirs(quality_dir, exist_ok=True)

    if should_generate_hls(mp4_path, quality_m3u8):
        video_bitrate = max(int(quality / 480 * 2000), 500)
        audio_bitrate = max(int(quality / 480 * 128), 64)

        subprocess.run([
            'ffmpeg', '-i', mp4_path,
            '-vf', f"scale={width}:{height}",
            '-c:a', 'aac',
            '-b:a', f'{audio_bitrate}k',
            '-c:v', 'h264',
            '-b:v', f'{video_bitrate}k',
            '-hls_time', '6',
            '-hls_playlist_type', 'vod',
            '-hls_list_size', '0',
            '-hls_segment_filename', os.path.join(quality_dir, 'hls-%03d.ts'),
            '-f', 'hls', quality_m3u8
        ])

    return os.path.join('static', videoname, f"{quality}p", 'hls.m3u8')

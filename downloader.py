from pytube import YouTube, Playlist
from pytube import request as pytube_request
import os
import time
import traceback
import re
import subprocess
import shutil
try:
    import yt_dlp
except Exception:
    yt_dlp = None

# Ensure default_headers exists on pytube.request (some installs / versions may not expose it)
_user_agent = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
)
if not hasattr(pytube_request, 'default_headers') or not isinstance(getattr(pytube_request, 'default_headers'), dict):
    pytube_request.default_headers = {}
pytube_request.default_headers.update({
    'User-Agent': _user_agent,
    'Accept-Language': 'en-US,en;q=0.9'
})

# Global variable for download path
DOWNLOAD_PATH = os.path.join(os.path.expanduser('~'), 'temp_downloads')

def check_path_exists():
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    return DOWNLOAD_PATH


def sanitize_filename(name: str, max_len: int = 200) -> str:
    """Return a filesystem-safe filename trimmed to max_len."""
    # Replace path separators and illegal chars
    name = re.sub(r'[\\/:*?"<>|\n\r]+', '_', name)
    name = name.strip()
    if len(name) > max_len:
        name = name[:max_len].rsplit(' ', 1)[0]
    return name


def ffmpeg_available() -> bool:
    return shutil.which('ffmpeg') is not None


def merge_video_audio(video_path: str, audio_path: str, out_path: str) -> None:
    """Merge video and audio into out_path using ffmpeg (lossless copy when possible)."""
    if not ffmpeg_available():
        raise RuntimeError('ffmpeg not found on PATH; required to merge video/audio')
    cmd = [
        'ffmpeg', '-y', '-i', video_path, '-i', audio_path,
        '-c', 'copy', out_path
    ]
    # Run merge and raise on error
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f'ffmpeg merge failed: {proc.stderr.decode(errors="ignore")}')

def download_playlist(playlist_url, download_type):
    playlist = Playlist(playlist_url)
    print(f'Downloading playlist: {playlist.title}')
    path= check_path_exists()
    global DOWNLOAD_PATH
    DOWNLOAD_PATH = path + '/' + playlist.title
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    for video_url in playlist.video_urls:
        print(f'Downloading video: {video_url}')
        download_video(video_url, download_type)
    

def download_video(url, download_type):
    try:
        # Add a progress callback to monitor download
        def on_progress(stream, chunk, bytes_remaining):
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percentage = (bytes_downloaded / total_size) * 100
            print(f'\rProgress: {percentage:.2f}%', end='')

        def on_complete(stream, file_path):
            print(f"\nDownload completed: {file_path}")

        # Initialize YouTube object with callbacks and retry mechanism
        last_exc = None
        for attempt in range(3):  # Try up to 3 times
            try:
                yt = YouTube(
                    url,
                    on_progress_callback=on_progress,
                    on_complete_callback=on_complete,
                    use_oauth=False,
                    allow_oauth_cache=True
                )
                # Verify the connection by accessing title
                _ = yt.title
                break  # If successful, break the retry loop
            except Exception as e:
                last_exc = e
                traceback.print_exc()
                if attempt == 2:  # Last attempt
                    print("pytube initialization failed after retries.")
                else:
                    print(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)  # Wait before retrying
        else:
            yt = None

        path = check_path_exists()

        # Fallback to yt-dlp if pytube couldn't initialize
        if (yt is None) or (getattr(yt, "title", None) is None):
            if yt_dlp is None:
                raise Exception(f"Failed to initialize YouTube object: {last_exc}")
            print("Falling back to yt-dlp to download the item...")
            ydl_opts = {
                'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': True,
            }
            if download_type == 'audio':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                })
            else:
                ydl_opts.update({'format': 'bestvideo+bestaudio/best', 'merge_output_format': 'mp4'})
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                print(f"yt-dlp download complete: {info.get('title')}")
            return
        
        path = check_path_exists()
        
        title_safe = sanitize_filename(yt.title)
        if download_type == 'video':
            print(f'\nFetching best video/audio for: {yt.title}')
            # Prefer DASH streams (separate video+audio) for best quality
            video_streams = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc()
            audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()

            # Pick best audio
            best_audio = audio_streams.first() if audio_streams else None

            # Pick best video (non-progressive) if available; otherwise fallback to progressive
            best_video = None
            if video_streams:
                best_video = video_streams.first()
            else:
                prog_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
                best_video = prog_streams.first() if prog_streams else None

            if best_video and best_audio and (best_video.itag != best_audio.itag):
                # Download video and audio separately then merge
                video_file = os.path.join(path, f"{title_safe}_video.{best_video.subtype}")
                audio_file = os.path.join(path, f"{title_safe}_audio.{best_audio.subtype}")
                out_file = os.path.join(path, f"{title_safe}.mp4")
                print(f'Downloading video stream: {getattr(best_video, "resolution", "unknown")}')
                best_video.download(output_path=path, filename=os.path.basename(video_file))
                print('Downloading best audio stream')
                best_audio.download(output_path=path, filename=os.path.basename(audio_file))
                print('Merging audio and video with ffmpeg')
                merge_video_audio(video_file, audio_file, out_file)
                # Optionally remove intermediate files
                try:
                    os.remove(video_file)
                    os.remove(audio_file)
                except Exception:
                    pass
            elif best_video:
                # Progressive or single-file video
                out_file = os.path.join(path, f"{title_safe}.{best_video.subtype}")
                print(f'Downloading progressive or single-file video: {getattr(best_video, "resolution", "unknown")}')
                best_video.download(output_path=path, filename=os.path.basename(out_file))
            else:
                raise Exception('No suitable video streams found')

        elif download_type == 'audio':
            print(f'\nFetching best audio for: {yt.title}')
            # Select best audio available
            audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
            if not audio_streams:
                raise Exception('No suitable audio streams found')
            best_audio = audio_streams.first()
            out_file = os.path.join(path, f"{title_safe}.{best_audio.subtype}")
            print(f'Downloading audio quality: {getattr(best_audio, "abr", "unknown")}')
            best_audio.download(output_path=path, filename=os.path.basename(out_file))
            # If user wants mp3 ensure ffmpeg available and convert
            # (we leave as-is by default to preserve best quality)
            
        print(f'\nDownload completed: {yt.title}')
        
    except Exception as e:
        print(f'\nError downloading {url}: {str(e)}')

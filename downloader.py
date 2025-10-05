from pytube import YouTube, Playlist
from pytube import request as pytube_request
import os
import time
import traceback
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
        
        if download_type == 'video':
            print(f'\nFetching video streams for: {yt.title}')
            # Get all streams and select the highest resolution mp4
            streams = yt.streams.filter(progressive=True, file_extension='mp4')
            if not streams:
                raise Exception("No suitable video streams found")
            stream = streams.get_highest_resolution()
            print(f'Downloading video quality: {stream.resolution}')
            stream.download(output_path=path, filename=f'{yt.title}.mp4')
            
        elif download_type == 'audio':
            print(f'\nFetching audio streams for: {yt.title}')
            # Get audio stream
            audio_streams = yt.streams.filter(only_audio=True)
            if not audio_streams:
                raise Exception("No suitable audio streams found")
            audio_stream = audio_streams.first()
            print('Downloading audio')
            audio_stream.download(output_path=path, filename=f'{yt.title}_audio.mp3')
            
        print(f'\nDownload completed: {yt.title}')
        
    except Exception as e:
        print(f'\nError downloading {url}: {str(e)}')

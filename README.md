# YTDownloader — YouTube downloader & converter

A lightweight, cross-platform command-line YouTube downloader that:

- Downloads videos and audio from YouTube
- Prefers the highest available quality (separate best video + best audio merged with ffmpeg)
- Falls back to `yt-dlp` if `pytube` fails to fetch metadata
- Works on Linux, macOS and Windows

This repository contains a simple CLI (`main.py`) and a `downloader.py` module which implements the download logic.

---

## What this project does

- Given a YouTube video or playlist URL, it detects whether the link is a single video or a playlist.
- For video downloads, it attempts to download the best available video and audio streams and merge them (using `ffmpeg`) to produce a high-quality MP4.
- For audio downloads, it fetches the best available audio-only stream. Conversion to MP3 is optional and can be added.
- If `pytube` cannot initialize (HTTP 400 or other issues), the script falls back to `yt-dlp` to perform the download.

---

## Requirements

- Python 3.8+
- pip
- ffmpeg (required if downloading separate video and audio streams and merging or converting audio)

Recommended:
- Create and use a virtual environment for installing Python packages.

---

## Installation (step-by-step)

1. Clone or download the repository:

```bash
# using HTTPS
git clone https://github.com/<your-username>/YTDownloader.git
cd YTDownloader
```

2. Create and activate a virtual environment (recommended):

Linux / macOS (bash):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

> Note: If you experience issues with the PyTube release, you can install the latest directly from the GitHub repo:
>
> ```bash
> pip install git+https://github.com/pytube/pytube
> ```

4. Install ffmpeg

- Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

- macOS (Homebrew)

```bash
brew install ffmpeg
```

- Windows

Download a static build from https://ffmpeg.org/download.html, then add the `bin` folder to your PATH.

---

## Usage

Basic CLI usage (dry-run):

```bash
python main.py "<YOUTUBE_URL>" --type audio --dry-run
```

Download audio (default):

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --type audio
```

Download video (best quality):

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --type video
```

Change the output directory:

```bash
python main.py "<YOUTUBE_URL>" --type video --out /path/to/output
```

For playlists, pass the playlist URL; the CLI will detect and download each video in sequence.

---

## Files of interest

- `main.py` — simple CLI entrypoint (argparse)
- `downloader.py` — core download logic (uses `pytube` and `yt-dlp` fallback)
- `requirements.txt` — python dependencies
- `INSTALL.txt` — beginner installation/run guide
- `.gitignore` — recommended ignores to avoid committing virtualenvs and temporary files

---

## Troubleshooting

- HTTP 400 errors with `pytube`:
  - Update `pytube` (`pip install --upgrade pytube`) or install from GitHub.
  - Ensure your network/proxy isn't blocking requests.
  - If `pytube` fails to initialize repeatedly the script will automatically fallback to `yt-dlp` (if installed).

- `ffmpeg` missing or merge fails:
  - Install `ffmpeg` and ensure it is on your PATH.
  - The script will raise a clear error if ffmpeg is required but missing.

- Filename/characters issues:
  - Filenames are sanitized, but if you notice odd file names please report the input URL and OS.

---


## Contributing

Contributions welcome. Open an issue or submit a pull request.

Thank you for using YTDownloader — let me know which enhancements you'd like next!

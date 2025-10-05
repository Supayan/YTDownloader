YouTube downloader and converter

This small project downloads YouTube videos or audio (using pytube) and falls back to yt-dlp when needed.

Quick start

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows (PowerShell/CMD)
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the CLI:

```bash
python -m __main__ "<YOUTUBE_URL>" --type audio
# or
python main.py "<YOUTUBE_URL>" --type video --out /path/to/out
```

Notes
- If pytube fails to fetch metadata, the code falls back to `yt-dlp` for downloading.
- For audio extraction, `ffmpeg` is required. Install using your package manager (apt, brew, choco).

Windows users: use the provided PowerShell/CMD command to activate your venv.

If you want, I can add a console_scripts entry so you can `pip install -e .` and get a `ytdl` command in your PATH.

## Uploading to GitHub

1. Initialize a new repository locally:

```bash
git init
git add .
git commit -m "Initial commit - YouTube downloader"
```

2. Create a new repository on GitHub (via website) and follow the instructions it shows to add a remote, for example:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

3. Add a descriptive README, license, and consider adding `requirements.txt` (already included).

That's it — your project is now stored on GitHub.

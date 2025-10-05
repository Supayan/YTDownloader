import argparse
import sys
import os
import downloader
import youtubePlaylist_checker


def main(argv=None):
    """CLI entrypoint for the downloader project.

    Usage examples:
      python -m __main__ <url> --type audio
      python main.py <url> --type video
    """
    parser = argparse.ArgumentParser(description='YouTube downloader (video/audio/playlist)')
    parser.add_argument('url', help='YouTube video or playlist URL')
    parser.add_argument('--type', '-t', choices=['audio', 'video'], default='audio', help='Download type')
    parser.add_argument('--out', '-o', default=None, help='Output directory (defaults to user temp_downloads)')
    parser.add_argument('--dry-run', action='store_true', help='Show actions without downloading')

    args = parser.parse_args(argv)

    # Allow override of the download path from CLI
    if args.out:
        # normalize path for cross-platform compatibility
        out_dir = os.path.abspath(os.path.expanduser(args.out))
        # create if missing
        os.makedirs(out_dir, exist_ok=True)
        # set module-global DOWNLOAD_PATH if present
        try:
            downloader.DOWNLOAD_PATH = out_dir
        except Exception:
            pass

    video_type = youtubePlaylist_checker.classify_youtube_url(args.url)
    print(f'Provided URL is classified as: {video_type}')

    if args.dry_run:
        print('Dry run mode - no downloads will be performed')
        if video_type == 'playlist':
            print('Would download playlist:', args.url)
        else:
            print('Would download video:', args.url)
        return 0

    if video_type == 'playlist':
        print('Playlist URL detected.')
        downloader.download_playlist(args.url, args.type)
    else:
        print('Single video URL detected.')
        downloader.download_video(args.url, args.type)


if __name__ == '__main__':
    sys.exit(main())
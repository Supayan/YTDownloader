from urllib.parse import urlparse, parse_qs

def classify_youtube_url(url):
    parts = urlparse(url)
    query = parse_qs(parts.query)
    domain = parts.netloc

    if 'playlist' in parts.path or ('list' in query and 'v' not in query):
        return 'playlist'
    elif 'watch' in parts.path or 'v' in query or 'youtu.be' in domain:
        if 'music.youtube.com' in domain:
            return 'song (YouTube Music)'
        return 'video'
    else:
        return 'unknown or unsupported'
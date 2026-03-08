import sys
import os
import time
import urllib.request
import urllib.parse
from html.parser import HTMLParser

class LinkParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag in ('a', 'img'):
            for attr, value in attrs:
                if attr in ('href', 'src') and value:
                    absolute_url = urllib.parse.urljoin(self.base_url, value)
                    self.urls.append(absolute_url)

def check_url(url):
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status
    except Exception as e:
        return str(e)

def push_ntfy(title, message):
    topic = os.getenv('NTFY_TOPIC')
    if not topic:
        print('[NTFY] No topic set, skipping push', file=sys.stderr)
        return
    server = os.getenv('NTFY_SERVER_URL', 'https://ntfy.sh')
    url = f"{server.rstrip('/')}/{topic}"
    data = message.encode('utf-8')
    headers = {'Title': title.encode('utf-8')}
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f'[NTFY] Push sent, status {response.status}')
            return response.status
    except Exception as e:
        print(f'[NTFY] Push failed: {e}', file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print('Usage: validator.py <base_url>')
        sys.exit(1)
    base_url = sys.argv[1]
    if not base_url.endswith('/'):
        base_url += '/'
    try:
        with urllib.request.urlopen(base_url, timeout=10) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f'Error fetching base URL {base_url}: {e}')
        sys.exit(1)

    parser = LinkParser(base_url)
    parser.feed(html)
    urls = set(parser.urls)
    print(f'Found {len(urls)} unique links to check on {base_url}')
    broken = []
    for url in urls:
        if not url.startswith('http'):
            continue
        status = check_url(url)
        if isinstance(status, str) or status >= 400:
            broken.append((url, status))
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    if broken:
        print('Broken links found:')
        for url, err in broken:
            print(f'- {url}: {err}')
        title = 'Broken Links Detected – The Hive'
        msg = f"{len(broken)} broken link(s) on {base_url} (checked at {timestamp}). First: {broken[0][0]}"
    else:
        print('All links are OK.')
        title = 'Site Health Check – The Hive'
        msg = f"All links are OK on {base_url} (checked at {timestamp})."

    # Attempt push if NTFY_TOPIC is set
    push_ntfy(title, msg)

    sys.exit(0 if not broken else 1)

if __name__ == '__main__':
    main()

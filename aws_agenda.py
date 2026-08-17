import json
import math
import os
import re
import requests

HUB_DIRECTORY_ID = "events-cards-interactive-summits-cards-interactive-events-summits-hub"
PAGE_SIZE = 8
DIR_ID_RE = re.compile(r'directoryId\\?":\\?"([a-zA-Z0-9\-]+)')

UNDISCOVERABLE = "undiscoverable"


def _session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    })
    return s


def discover_directory_id(agenda_url, s=None):
    s = s or _session()
    html = s.get(agenda_url, timeout=20).text
    for match in DIR_ID_RE.finditer(html):
        directory_id = match.group(1)
        if directory_id != HUB_DIRECTORY_ID:
            return directory_id
    return None


def fetch_sessions(event, out_path=None, on_progress=None):
    on_progress = on_progress or (lambda stage: None)
    out_path = out_path or f"data/{event['slug']}/sessions.jsonl"
    s = _session()

    on_progress("Looking up event's session directory...")
    directory_id = discover_directory_id(event['agenda_url'], s)
    if directory_id is None:
        return UNDISCOVERABLE

    def fetch_page(page):
        return s.get('https://aws.amazon.com/api/dirs/items/search', params={
            'item.directoryId': directory_id,
            'item.locale': 'en_US',
            'sort_by': 'item.dateCreated',
            'sort_order': 'asc',
            'size': PAGE_SIZE,
            'page': page,
        }).json()

    first = fetch_page(0)
    total_hits = first.get('metadata', {}).get('totalHits', 0)
    if total_hits == 0:
        return None

    total_pages = math.ceil(total_hits / PAGE_SIZE)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        for page in range(total_pages):
            on_progress(f"Fetching sessions: page {page + 1}/{total_pages}")
            data = first if page == 0 else fetch_page(page)
            for item in data.get('items', []):
                f.write(json.dumps(item) + '\n')

    event_meta_path = os.path.join(os.path.dirname(out_path), "event.json")
    existing_meta = {}
    if os.path.exists(event_meta_path):
        with open(event_meta_path) as f:
            existing_meta = json.load(f)
    with open(event_meta_path, 'w') as f:
        json.dump({
            **existing_meta,
            'title': event['title'],
            'date': event['date'],
            'location': event['location'],
            'agenda_url': event['agenda_url'],
        }, f, indent=2)

    return total_hits, out_path

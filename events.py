import math
import re
import requests

HUB_DIRECTORY_ID = "events-cards-interactive-summits-cards-interactive-events-summits-hub"
PAGE_SIZE = 10


def _city_from(cta_link):
    return re.split(r"[/]", cta_link.rstrip("/"))[-1]


def _agenda_url_from(cta_link):
    base = cta_link if cta_link.startswith('http') else f'https://aws.amazon.com{cta_link}'
    return base.rstrip('/') + '/agenda/'


def fetch_events(on_progress=None):
    on_progress = on_progress or (lambda status: None)
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    })

    def fetch_page(page):
        return s.get('https://aws.amazon.com/api/dirs/items/search', params={
            'item.directoryId': HUB_DIRECTORY_ID,
            'item.locale': 'en_US',
            'sort_by': 'item.dateCreated',
            'sort_order': 'asc',
            'size': PAGE_SIZE,
            'page': page,
        }).json()

    on_progress("Fetching event list...")
    first = fetch_page(0)
    total_pages = math.ceil(first.get('metadata', {}).get('totalHits', 0) / PAGE_SIZE)

    events = []
    for page in range(total_pages):
        on_progress(f"Fetching event list: page {page + 1}/{total_pages}...")
        data = first if page == 0 else fetch_page(page)
        for entry in data.get('items', []):
            fields = entry['item']['additionalFields']
            city = _city_from(fields['ctaLink'])
            year = fields['date'].split('-')[0]
            events.append({
                'title': fields['title'].strip(),
                'date': fields['date'],
                'location': city.replace('-', ' ').title(),
                'slug': f"summit-{city}-{year}",
                'agenda_url': _agenda_url_from(fields['ctaLink']),
            })

    events.sort(key=lambda e: e['location'])
    return events

import sys
import re
from datetime import datetime
sys.path.insert(0, '/a0/usr/workdir/web-scraper/scripts')
import scraper

URL = 'https://www.waheagle.com/'
soup = scraper.scrape_url(URL)
if not soup:
    print('fetch failed')
    sys.exit(1)

# Copy of extract_sheriff_report with debug
entries = []
sheriff_heading = None
for heading in soup.find_all(['h1','h2','h3','h4','h5','h6']):
    txt = heading.get_text().strip().lower()
    print(f'Checking heading: {heading.name} -> {txt}')
    if 'sheriff' in txt and ('report' in txt or 'log' in txt or 'blotter' in txt):
        sheriff_heading = heading
        print(' -> matched!')
        break

if not sheriff_heading:
    print('No Sheriff heading found')
else:
    print('Found heading:', sheriff_heading.name, sheriff_heading.get_text().strip())
    next_elem = sheriff_heading.find_next()
    list_elem = None
    count = 0
    while next_elem and count < 20:
        print(f'Next element: {next_elem.name}')
        if next_elem.name in ['ul','ol']:
            list_elem = next_elem
            print(' -> Found list!')
            break
        if next_elem.name in ['h1','h2','h3','h4','h5','h6']:
            print(' -> hit another heading, stop')
            break
        next_elem = next_elem.find_next()
        count += 1
    if list_elem:
        print('List element found, scanning li')
        for li in list_elem.find_all('li', recursive=False):
            text = li.get_text(separator=' ', strip=True)
            print(' - li text:', text[:100])
            # parse date
            date_text = text
            m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})|(\d{1,2})-(\d{1,2})-(\d{4})|(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),\s+(\d{4})|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})', text, re.I)
            if m:
                print('   -> date pattern matched')
            entries.append({'text': text, 'date': None})
        print(f'Total entries extracted: {len(entries)}')
    else:
        print('No list found, fallback not implemented')

# Filter to preceding week
report_date = datetime.now().date()
week_ago = report_date - timedelta(days=7)
filtered = []
for e in entries:
    if e['date'] is None:
        filtered.append(e)
    else:
        d = e['date']
        if week_ago <= d < report_date:
            filtered.append(e)
print(f'Filtered to {len(filtered)} entries within preceding week ({week_ago} to {report_date})')
